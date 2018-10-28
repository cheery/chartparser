import chartparser
from chartparser import (
    Terminal, Nonterminal, Rule,
    preprocess)
import visualizer

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

    input_strings = [
        "x",
        "xxx",
        "xxxxxx"
    ]

    visualizer.print_grammar(user_grammar)

    parser = preprocess(user_grammar, accept)()
    visualizer.print_nnf_grammar(parser.grammar)

    input_string = visualizer.select_input_string(input_strings)

    visualizer.step_through(parser, terminals, input_string)

if __name__=='__main__':
    main()
