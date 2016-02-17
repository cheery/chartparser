def main():
    s = Nonterminal('s')
    a = Nonterminal('a')
    b = Nonterminal('b')
    x = Terminal('x')

    terminals = {"x": x}

    accept = s
    user_grammar = [
        Rule(s, [s, a]),
        Rule(s, []),
        Rule(a, [x]),
    ]

    parser = preprocess(user_grammar, accept)()
    input_string = "xxxxxx"
    for token in input_string:
        parser.step(terminals[token], token)
    print parser.accepted, parser.expect, parser.expecting(x)
    print parser.traverse(lambda x, a: '(' + ' '.join(a) + ')', lambda x: "")

def preprocess(user_grammar, accept):
    nullable = find_nullable(user_grammar)
    grammar = {}
    blankset = {}
    for rule in build_nnf(user_grammar, nullable):
        if len(rule.rhs) == 0:
            try:
                blankset[rule.lhs].append(rule.annotation.rule)
            except KeyError as k:
                blankset[rule.lhs] = [rule.annotation.rule]
        else:
            try:
                grammar[rule.lhs].append(rule)
            except KeyError as k:
                grammar[rule.lhs] = [rule]
    def new_parser(accept=accept):
        parser = Parser(grammar, accept, [])
        # In an earley parser that uses NNF, empty input is a special case, that is taken care of here.
        if accept in nullable:
            for rule in user_grammar:
                if rule.lhs == accept and all(x in nullable for x in rule.rhs):
                    parser.output.append(Rule(accept, [], NNF(rule, [False for x in rule.rhs])))
        # The first chart column
        transitions = {}
        nodes = {}
        current = []
        prediction(current, nodes, grammar, 0, accept)
        for eim in current:
            prediction(current, nodes, grammar, 0, eim.postdot())
            cache_transitions(transitions, eim, None)
        parser.chart.append(transitions)
        return parser
    new_parser.blankset = blankset
    new_parser.nullable = nullable
    return new_parser

def default_ambiguity_resolution(sppf):
    raise Exception(sppf)

class Parser(object):
    def __init__(self, grammar, accept, output):
        self.chart = []
        self.grammar = grammar
        self.accept = accept
        self.output = output

    def step(self, term, token):
        # completions proceed in non-deterministic manner, until
        # everything has been completed.
        current = []
        transitions = {}
        nodes = {}
        location = len(self.chart)
        output = []

        bottom = SPPF(location-1, location, token, None)
        for eim, bb in self.chart[location-1][term]:
            shift_eim(current, nodes, eim, location, bb, bottom)
        for eim in current:
            # reduction
            cc = nodes[eim]
            if eim.is_completed():
                for before, bb in self.chart[eim.origin].get(eim.rule.lhs, ()):
                    shift_eim(current, nodes, before, location, bb, cc)
                if eim.rule.lhs == self.accept and eim.origin == 0:
                    output.append(cc)
            prediction(current, nodes, self.grammar, location, eim.postdot())
            cache_transitions(transitions, eim, cc)
        self.chart.append(transitions)
        self.output = output

    @property
    def accepted(self):
        return len(self.output) > 0

    @property
    def expect(self):
        return self.chart[-1].keys()

    def expecting(self, symbol):
        return symbol in self.chart[-1]

    def traverse(self, postorder_callback, blank_callback, resolve_ambiguity=default_ambiguity_resolution):
        if len(self.output) > 1:
            sppf = resolve_ambiguity(None, self.output)
        else:
            sppf = self.output[0]
        return traverse_sppf(sppf, postorder_callback, blank_callback, resolve_ambiguity)

def prediction(current, nodes, grammar, location, postdot):
    if isinstance(postdot, Nonterminal):
        for rule in grammar.get(postdot, ()):
            eim = EIM(rule, 0, location)
            if not eim in nodes:
                nodes[eim] = None
                current.append(eim)

def cache_transitions(transitions, eim, cc):
    postdot = eim.postdot()
    if not eim.is_completed():
        try:
            transitions[postdot].append((eim, cc))
        except KeyError as k:
            transitions[postdot] = [(eim, cc)]

def shift_eim(current, nodes, eim, location, bb, cc):
    eim = eim.next()
    try:
        sppf = nodes[eim]
        sppf.insert(bb, cc)
    except KeyError as k:
        assert eim.pos != 0
        nodes[eim] = sppf = SPPF(eim.origin, location, eim.rule, Link(bb, cc))
        current.append(eim)

def build_nnf(grammar, nullable):
    for rule in grammar:
        order = sum(x in nullable for x in rule.rhs)
        for i in range(1 << order):
            yield nihilist_rule(rule, i, nullable)

def nihilist_rule(rule, index, nullable):
    present = []
    rhs = []
    for symbol in rule.rhs:
        shift = True
        if symbol in nullable:
            if index & 1 == 0:
                shift = False
            index >>= 1
        present.append(shift)
        if shift:
            rhs.append(symbol)
    return Rule(rule.lhs, rhs, NNF(rule, present))

def detect_right_recursion(grammar):
    edges = []
    for rule in grammar:
        right = rule.rhs[-1] if len(rule.rhs) > 0 else None
        row = []
        for other in grammar:
            row.append(other.lhs == right)
        edges.append(row)
    warshall_transitive_closure(edges)
    return set(rule for i, rule in enumerate(grammar) if edges[i][i])

def warshall_transitive_closure(a):
    n = len(a)
    for k in range(n):
        for i in range(n):
            if not a[i][k]:
                continue
            for j in range(n):
                if not a[k][j]:
                    continue
                a[i][j] = True
    return a

def find_nullable(grammar):
    nullable = set()
    queue = []
    def new_nullable(symbol):
        if symbol not in nullable:
            nullable.add(symbol)
            queue.append(symbol)

    inverse_lookup = {}
    def new_lookup(index, symbol):
        if symbol in inverse_lookup:
            inverse_lookup[symbol].append(index)
        else:
            inverse_lookup[symbol] = [index]

    nonterminals = []
    nonnullables = []

    for rule in grammar:
        if len(rule) == 0:
            new_nullable(rule.lhs)
        elif all(isinstance(x, Nonterminal) for x in rule.rhs):
            index = len(nonnullables)
            for x in rule.rhs:
                if x != rule.lhs:
                    new_lookup(index, x)
            nonterminals.append(rule.lhs)
            nonnullables.append(sum(x != rule.lhs for x in rule.rhs))

    for n in queue:
        for i in inverse_lookup.get(n, ()):
            nonnullables[i] -= 1
            if nonnullables[i] == 0:
                new_nullable(nonterminals[i])

    return nullable

def traverse_sppf(sppf, postorder_callback, blank_callback, resolve_ambiguity):
    rcount = 1
    sstack = []
    rstack = []
    stack = [sppf]
    while len(stack) > 0:
        sppf = stack.pop()
        if sppf.is_leaf():
            sstack.append(sppf.cell)
            rcount -= 1
        else:
            result = sppf.single()
            if result is None:
                result = resolve_ambiguity(sppf)
            rstack.append((rcount - 1, len(result), sppf))
            rcount = len(result)
            stack.extend(reversed(result))
        while rcount == 0 and len(rstack) > 0:
            rcount, rlen, sppf = rstack.pop(-1)
            rule, args = expand(sppf.cell, blank_callback, (sstack.pop(i-rlen) for i in range(rlen)))
            sstack.append(postorder_callback(rule, args))
    assert len(sstack) == 1
    return sstack[0]

def expand(cell, blank_callback, seq):
    if isinstance(cell.annotation, NNF):
        nnf = cell.annotation
        result = []
        for i, p in enumerate(nnf.present):
            if p:
                result.append(seq.next())
            else:
                result.append(blank_callback(nnf.rule.rhs[i]))
        return nnf.rule, result
    return cell, list(seq)

class Rule(object):
    def __init__(self, lhs, rhs, annotation=None):
        self.lhs = lhs
        self.rhs = rhs
        self.annotation = annotation

    def __len__(self):
        return len(self.rhs)

    def __repr__(self):
        return "{} -> {}".format(
            self.lhs,
            ' '.join(map(str, self.rhs)))

# Nihilist normal form
class NNF(object):
    def __init__(self, rule, present):
        self.rule = rule
        self.present = present          # tells which fields are present.

# Earlier I did not separate terminals from
# non-terminals because it was not strictly
# necessary. That turned out to confuse
# when designing grammars.
class Terminal(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "T{!r}".format(self.name)

class Nonterminal(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{!s}".format(self.name)

# The chart consists explicitly from earley items.
class EIM(object):
    def __init__(self, rule, pos, origin):
        self.rule = rule
        self.pos = pos
        self.origin = origin
        assert 0 <= pos <= len(rule)

    def postdot(self):
        if self.pos < len(self.rule):
            return self.rule.rhs[self.pos]
        return None

    def next(self):
        if self.postdot() is not None:
            return EIM(self.rule, self.pos + 1, self.origin)
        return None

    def penult(self):
        if self.pos + 1 == len(self.rule):
            return self.postdot()

    def is_predicted(self):
        return self.pos == 0

    def is_confirmed(self):
        return self.pos > 0

    def is_completed(self):
        return self.pos == len(self.rule)

    def __hash__(self):
        return hash((self.rule, self.pos, self.origin))

    def __eq__(self, other):
        return isinstance(other, EIM) and self.rule == other.rule and self.pos == other.pos and self.origin == other.origin

    def __repr__(self):
        if isinstance(self.rule, Rule):
            lhs = repr(self.rule.lhs)
            pre = ' '.join(map(repr, self.rule.rhs[:self.pos]))
            pos = ' '.join(map(repr, self.rule.rhs[self.pos:]))
            return "{} -> {} * {} : {}".format(lhs, pre, pos, self.origin)
        return object.__repr__(self)

# Shared packed parse forest
class SPPF(object):
    def __init__(self, start, stop, cell, link):
        self.start = start
        self.stop = stop
        self.cell = cell
        self.link = link

    def is_leaf(self):
        return self.link is None

    def insert(self, left, right):
        if self.link is None:
            self.link = Link(left, right)
            return self.link
        link = self.link
        while True:
            if link.left == left and link.right == right:
                return link
            if link.link is None:
                link.link = Link(left, right)
                return link.link
            link = link.link

    def single(self):
        result = []
        link = self.link
        while link.left is not None:
            if link.link is not None:
                return None
            result.append(link.right)
            link = link.left.link
        result.append(link.right)
        result.reverse()
        return result

    def __iter__(self):
        finger = []
        # To produce all parses, the sppf is fingered through.
        link = self.link
        while len(finger) > 0 or link is not None:
            while link.left is not None:
                finger.append(link)
                link = link.left.link
            # Now the link contains the head, while the tail is in the finger list.
            while link is not None:
                result = [link.right]
                result.extend(x.right for x in reversed(finger))
                yield result
                link = link.link
            # Now some portion of the finger is already iterated, and should be removed.
            while len(finger) > 0 and link is None:
                link = finger.pop().link

    def __repr__(self):
        return "[{}:{}] {}".format(self.start, self.stop, self.cell)

class Link(object):
    def __init__(self, left, right, link=None):
        self.left = left
        self.right = right
        self.link = link

if __name__=="__main__":
    main()
