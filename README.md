# Chart parser

This parser will soon replace the custom one in lever/, until then it has not been throroughly tested. Early users beware for bugs.

Imagine you'd have to make sense of some input, commonly an user interaction. You get a sequence of symbols and have to recognize some structure for it. This is when you need a parsing library. Chart parsers are straightforward but potentially resource consumptive tool for this. For small inputs or simple languages, they're often sufficient.

Chart parser takes in a Context-free grammar and the input sequence.

Here's how to input a context-free grammar that the chartparser can read:

    from chartparser import NonTerminal, Terminal, Rule

    s, a = Nonterminal('s'), Nonterminal('a')
    x = Terminal('x')
    grammar = [
        Rule(s, [s, a]),
        Rule(s, []),
        Rule(a, [x]),
    ]

Note that you can pass a third parameter to Rule, that will be bound to `annotation`, how you use this field is entirely up to you.

Chart parsers are not usually preprocessing-free, but the preprocessing tends to happen in such short time that nobody worries about it. Here's how to form a parser:

    from chartparser preprocess

    parser = preprocess(grammar, accept=s)()

Note that `preprocess` gives a function that you can call to instantiate a parser. This is done so you can parse many inputs with single preprocessing step.

Attention: Many chart parsers can allow you to select the symbol when you start parsing, rather than when you preprocess the grammar. You are required to supply the default symbol in `preprocess`. But this is also acceptable:

    new_parser = preprocess(grammar, accept=s)
    parser = new_parser(accept=a)

If this is not possible on some other variation of this library, the `new_parser()` takes a liberty to crash on argument error.

The parser contains several interfaces that you probably need for your usecase. The first one is a `.step`, and you use it to give the input into the parser. The first argument is the symbol this item represents. It can be both Terminal and Nonterminal. The second is the token put into this position. Here's an example that uses makeshift input:

    terminals = {"x": x}
    input_string = "xxxxxx"
    for token in input_string:
        parser.step(terminals[token], token)

Additionally you have following interfaces that are available during parsing:

* `parser.accepted` tells whether the input so far can be accepted and traversed.
* `parser.expect` contains terminals and nonterminals that when `.step` next will result in a non-empty parsing state.
* `parser.expecting(x)` can be used to query whether parsing can `.step` with the given symbol.

Finally when you've finished your input, you want to make sense of it by `.traverse`. Here's how to do it:

    def postorder_call(rule, rhs):
        return '(' + ' '.join(rhs) + ')'
    def blank(symbol):
        return ''
    def ambiguous(sppf):
        for p in sppf:
            print p
        raise Exception("ambiguous parse")
        # This may also choose one interpretation among ambiguous results.
        # in that case return one of 'p' from this function.
    result = parser.traverse(postorder_call, blank, ambiguous)

Note that blank rules will never reach postorder_call. Instead the `blank` is called with the appropriate symbol. This is done so the chart parser doesn't need to produce permutations of the empty rules, if they appear. If you rather want to derive empty objects from the blank rules, you can obtain `.nullable` and `.blankset` during preprocessing:

    new_parser = preprocess(grammar, accept=s)
    print new_parser.blankset
    print new_parser.nullable

## Supported

I make a promise to respond on support issues as long as I keep writing python code. I also try to keep the interface described in this readme mostly unchanged from what it is now. I did lot of care to get it this clean.

The parsing library exposes lot of other details you may need necessary to use. For example, my single traversing approach might not satisfy every urge. Those details may change in future.

## Origins

This module is using [the work of Jeffrey Kegler](http://jeffreykegler.github.io/Marpa-web-site/). He introduced these concepts to me, and the papers about Marpa helped me to refine an adaptation of the parser on python.
