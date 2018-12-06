import chartparser
from chartparser import (
    Terminal, Nonterminal, Rule,
    preprocess)

command = Nonterminal('start')

look = Terminal('look')
go = Terminal('go')
to_ = Terminal('to')
inventory = Terminal('inventory')

place = Terminal('some place')

token_table = {
    "look": look,
    "go": go,
    "to": to_,
    "inventory": inventory,
    "inv":       inventory,
}

grammar = [
    Rule(command, [look], annotation='look'),
    Rule(command, [go, to_], annotation="goto?"),
    Rule(command, [go, to_, place], annotation="goto"),
    Rule(command, [inventory], annotation='inventory'),
]

class ENVIRONMENT:
    def __init__(self):
        self.current_room = first_room
        self.inventory = set(['axe', 'lamp', 'toilet'])

    def get_grammar(self):
        return grammar

class EMPTY_ROOM:
    description = "You are in an empty room"
    def __init__(self):
        self.passages = {}
        self.items = []

first_room = EMPTY_ROOM()
second_room = EMPTY_ROOM()
second_room.description = "You are in an another empty room"

first_room.passages  = {"hole": second_room}
first_room.items = set(['some thing', 'other thing'])

second_room.passages = {"hole": first_room}
second_room.items = set(['dangerous thing', 'weird thing'])


def main():
    print "Welcome to the empty room"
    environment = ENVIRONMENT()

    while True:
        try:
            action = attempted_parse_of_input(environment)
        except EOFError as eof:
            print "okay."
            return
        if action is None:
            print "what do you mean?"
        else:
            action(environment)

def attempted_parse_of_input(environment):
    language = preprocess(environment.get_grammar(), command)
    parser = language()

    input_string = raw_input("> ")
    for word in input_string.strip().split(" "):
        cleaned_word = word.strip().lower()
        try:
            token = recognize_word(environment, cleaned_word)
            parser.step(token, cleaned_word)
        except KeyError as ke:
            print "at word {!r}".format(word)
            parser_error_message(parser)
            return None
    if parser.accepted:
        return parser.traverse(
            rule_traverse,
            empty_traverse)
    else:
        print "at end of the sentence"
        parser_error_message(parser)
        return None

def recognize_word(environment, cleaned_word):
    if cleaned_word in environment.current_room.passages:
        return place
    return token_table[cleaned_word]

def parser_error_message(parser):
    expect = list(parser.expect)
    if len(expect) == 0:
        print "EXPECTED nothing"
    else:
        print "EXPECTED one of"
        for token in expect:
            print "  {}".format(token)

def rule_traverse(rule, arguments):
    if rule.annotation == 'look':
        return _look_around_
    elif rule.annotation == 'goto?':
        def _goto_where_(environment):
            print "go to where? places to go:"
            for place in environment.current_room.passages.keys():
                print "  {}".format(place)
        return _goto_where_
    elif rule.annotation == 'goto':
        def _goto_(environment):
            print "you go to", arguments[2]
            previous_room = environment.current_room
            environment.current_room = previous_room.passages[arguments[2]]
            _look_around_(environment)
        return _goto_
    elif rule.annotation == 'inventory':
        def _print_inventory_(environment):
            print "you have items"
            for item in environment.inventory:
                print "  {}".format(item)
        return _print_inventory_
    elif rule.annotation == 'place':
        return arguments[0]
    else:
        parse_tree = rule.annotation + '(' + ' '.join(
            repr(item) for item in arguments) + ')'
        def _placeholder_(environment):
            print "not implemented"
            print parse_tree
        return _placeholder_

def empty_traverse(rule):
    def _placeholder_(environment):
        print "not implemented (empty rule)"
        print rule
    return _placeholder_

def _look_around_(environment):
    print environment.current_room.description
    if len(environment.current_room.items) > 0:
        print "there are items"
        for item in environment.current_room.items:
            print "  {}".format(item)

if __name__=='__main__':
    main()
