#import traceback # For printing tracebacks

# This visualizer was written with the purpose to help
# study of the parsing algorithm.

# 1. It prints out your grammar,
# 2. then it prints the preprocessing results.
# 3. Finally it lets you choose among the input strings and
# 4. step the parser through.
# 4.b. If the parsing step encounters an error,
#      the error and trace is printed and the parser considered lost.
# 4.c. Asks for more input or stops if no string given.

# The example grammars import this utility as a module.
# But you should expect there can be some global values stored later
# this is more like its own program.

# The preprocessed items are annotated with NNF nodes
# and connected to the input grammar that way.
# I avoided printing NNF items in the simple outputs because
# it would have required more printout.

def print_grammar(grammar):
    print "THE INPUT GRAMMAR"
    for rule in grammar:
        print "  {0.lhs} -> {1}".format(rule,
            " ".join(repr(sym) for sym in rule.rhs))
    raw_input("press return and continue")

def print_nnf_grammar(grammar):
    print "THE PREPROCESSED GRAMMAR"
    for lhs, rules in grammar.iteritems():
        for rule in rules:
            print "  {0.lhs} -> {1}".format(rule,
                " ".join(repr(sym) for sym in rule.rhs))
    raw_input("press return and continue")

# Preprocessing also contains the blankset,
# a set of nonterminals that can produce empty sequences.
# We are not printing that for now.

def select_input_string(input_strings):
    print "Select the input string"
    for index, string in enumerate(input_strings):
        print "  [{}] {!r}".format(index, string)
    print "  [a] write your own string"
    choice = raw_input("? ")
    if choice.lower() == 'a':
        return raw_input("input string: ")
    else:
        try:
            return input_strings[int(choice)]
        except ValueError as error:
            print "error: {}".format(error)
            return select_input_string(input_strings)
        except IndexError as error:
            print "error: no such option"
            return select_input_string(input_strings)

def step_through(parser, terminals, input_string):
    while len(input_string) > 0:
        for token in input_string:
            print_parsing_state(parser)
            print "next token: {}".format(terminals[token])
            raw_input("press return and continue")
            #try:
            parser.step(terminals[token], token)
            #except Exception as error:
            #    traceback.print_exc()
            #    return
        print_parsing_state(parser, True)
        input_string = raw_input("more input string? ")
    
def print_parsing_state(parser, final=False):
    print "CHART {}".format(len(parser.chart)-1)
    for term, eims in parser.chart[-1].iteritems():
        for eim, bb in eims:
            if bb is None:
                print "  {}".format(eim)
            else:
                print "  {} [{}]".format(eim, bb)
    if parser.accepted:
        print "INPUT ACCEPTED"
        if not final:
            for cc in parser.output:
                print "  {}".format(cc)
        else:
            print " ", parser.traverse(lambda x, a: '(' + ' '.join(a) + ')', lambda x: "")
