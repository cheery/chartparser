import chartparser
from chartparser import (
    Terminal, Nonterminal, Rule,
    preprocess)
import visualizer

def main():
    d0 = Terminal('0')
    d1 = Terminal('1')
    d2 = Terminal('2')
    d3 = Terminal('3')
    d4 = Terminal('4')
    d5 = Terminal('5')
    d6 = Terminal('6')
    d7 = Terminal('7')
    d8 = Terminal('8')
    d9 = Terminal('9')
    plus = Terminal('+')
    minus = Terminal('-')
    div = Terminal('/')
    mul = Terminal('*')
    open_ = Terminal('(')
    close_ = Terminal(')')
    dot = Terminal('.')
    start = Nonterminal('start')
    expr = Nonterminal('expr')
    term = Nonterminal('term')
    factor = Nonterminal('factor')
    integer = Nonterminal('integer')
    digit = Nonterminal('digit')

    grammar = [
        Rule(start, [expr]),
        Rule(expr, [term, plus,expr]),
        Rule(expr, [term, minus,expr]),
        Rule(expr, [term]),
        Rule(term, [factor]), # This rule was missing in issue/1
        Rule(factor, [plus, factor]),
        Rule(factor, [minus, factor]),
        Rule(factor, [open_, expr, close_]),
        Rule(factor, [integer]),
        Rule(factor, [integer, dot, integer]),
        Rule(integer, [digit, integer]),
        Rule(integer, [digit]),
        Rule(digit, [d0]),
        Rule(digit, [d1]),
        Rule(digit, [d2]),
        Rule(digit, [d3]),
        Rule(digit, [d4]),
        Rule(digit, [d5]),
        Rule(digit, [d6]),
        Rule(digit, [d7]),
        Rule(digit, [d8]),
        Rule(digit, [d9]),
    ]

    accept = start
    terminals = {
            "0": d0,
            "1": d1,
            "2": d2,
            "3": d3,
            "4": d4,
            "5": d5,
            "6": d6,
            "7": d7,
            "8": d8,
            "9": d9,
            "+": plus,
            "-": minus,
            "/": div,
            "*": mul,
            "(": open_,
            ")": close_,
            ".": dot,
            }

    user_grammar = grammar

    input_strings = [
        "321345",
    ]

    visualizer.print_grammar(user_grammar)

    parser = preprocess(user_grammar, accept)()
    visualizer.print_nnf_grammar(parser.grammar)

    input_string = visualizer.select_input_string(input_strings)

    visualizer.step_through(parser, terminals, input_string)

if __name__=='__main__':
    main()
