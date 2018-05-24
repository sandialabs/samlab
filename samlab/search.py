# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from pyparsing import *

def parser():
    """Return an object that can parse search expressions.

    Returns
    -------
    parser: `pyparsing.ParserElement`
        The returned object can be used to parse a search expression using
        `parser.parse(expression)`, which will return a parse tree.  Use the
        `accept(visitor)` method of the parse tree to access its contents.
    """

    class ParseElement(object):
        def accept(self, visitor):
            raise NotImplementedError()

    class UnaryOperation(ParseElement):
        def __init__(self, tokens):
            self.operation, self.operand = tokens[0]

        def __repr__(self):
            return "%s(%s)" % (self.operation, self.operand)

    class BinaryOperation(ParseElement):
        def __init__(self, tokens):
            self.operation = tokens[0][1]
            self.operands = tokens[0][0::2]

        def __repr__(self):
            return "%s(%s)" % (self.operation, ", ".join([str(operand) for operand in self.operands]))

    class SearchAnd(BinaryOperation):
        def accept(self, visitor):
            visitor.visit_and(self.operands)
            return visitor

    class SearchNot(UnaryOperation):
        def accept(self, visitor):
            visitor.visit_not(self.operand)
            return visitor

    class SearchOr(BinaryOperation):
        def accept(self, visitor):
            visitor.visit_or(self.operands)
            return visitor

    class SearchTerm(ParseElement):
        def __init__(self, tokens):
            self.term = tokens[0]

        def accept(self, visitor):
            visitor.visit_term(self.term)
            return visitor

        def __repr__(self):
            return repr(self.term)

    class SearchParser(object):
        def __init__(self, search_expression):
            self._search_expression = search_expression

        def parse(self, expression):
            return self._search_expression.parseString(expression, parseAll=True)[0]

    search_term = Word(printables, excludeChars='"') | QuotedString(quoteChar='"')
    search_term.setParseAction(SearchTerm)

    search_expression = infixNotation(search_term, [
        (CaselessKeyword("not")("not"), 1, opAssoc.RIGHT, SearchNot),
        (CaselessKeyword("and")("and"), 2, opAssoc.LEFT, SearchAnd),
        (CaselessKeyword("or")("or"), 2, opAssoc.LEFT, SearchOr),
    ])

    return SearchParser(search_expression)

if __name__ == "__main__":
    p = parser()

    class Visitor(object):
        def __init__(self):
            self._stack = []

        @property
        def stack(self):
            return self._stack[0]

        def visit_and(self, operands):
            index = len(self._stack)
            for operand in operands:
                operand.accept(self)
            frame = [["and"] + self._stack[index:]]
            self._stack = self._stack[:index] + frame

        def visit_not(self, operand):
            index = len(self._stack)
            operand.accept(self)
            frame = [["not"] + self._stack[index:]]
            self._stack = self._stack[:index] + frame

        def visit_or(self, operands):
            index = len(self._stack)
            for operand in operands:
                operand.accept(self)
            frame = [["or"] + self._stack[index:]]
            self._stack = self._stack[:index] + frame

        def visit_term(self, term):
            self._stack.append([term])


    for test in [
        'foo',
        '"foo bar"',
        'label:foo',
        '"label:foo"',
        '"label:foo bar"',
        'not foo',
        'not "foo bar"',
        'not "not"',
        'foo and bar',
        'foo or bar',
        'foo and bar and baz',
        'foo and bar or baz',
        'foo and (bar or baz)',
        'foo AND bar',
        'foo and not bar',
        'not foo and not bar',
        'not (foo or bar)',
        ]:
        results = p.parse(test)
        print(test, "->", results)

        print(results.accept(Visitor()).stack)
        print()
