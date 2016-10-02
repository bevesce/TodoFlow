from __future__ import unicode_literals

import unittest
import datetime as dt

from todoflow.query_lexer import QueryLexer
from todoflow.query_lexer import Token


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.lex = QueryLexer()

    def tokens(self, text):
        self.tokens = self.lex.run(text)
        return self

    def are(self, tokens):
        self.assertEqual(
            self.tokens,
            [Token(t, v) for t, v in tokens]
        )

    def test_attribute(self):
        self.tokens('@text').are([
            ('attribute', 'text')
        ])

    def test_word_operator(self):
        self.tokens('and').are([
            ('operator', 'and')
        ])

    def test_shortcut(self):
        self.tokens('project').are([
            ('shortcut', 'project')
        ])

    def test_word(self):
        self.tokens('test').are([
            ('search term', 'test')
        ])

    def test_opeartor(self):
        self.tokens('<').are([
            ('operator', '<')
        ])

    def test_two_char_opertor(self):
        self.tokens('<=').are([
            ('operator', '<=')
        ])

    def test_relation_modifier(self):
        self.tokens('[d]').are([
            ('relation modifier', 'd')
        ])

    def test_wild_card(self):
        self.tokens('*').are([
            ('wild card', '*')
        ])

    def test_no_wild_card_in_search_term(self):
        self.tokens('r*r').are([
            ('search term', 'r*r')
        ])

    def test_slice(self):
        self.tokens('[1:2]').are([
            ('slice', '1:2')
        ])

    def test_start_slice(self):
        self.tokens('[1:]').are([
            ('slice', '1:')
        ])

    def test_end_slice(self):
        self.tokens('[:2]').are([
            ('slice', ':2')
        ])

    def test_index_slice(self):
        self.tokens('[2]').are([
            ('slice', '2')
        ])

    def test_axis_direct(self):
        self.tokens('/').are([
            ('axis', '/')
        ])

    def test_axis_descendant(self):
        self.tokens('//').are([
            ('axis', '//')
        ])

    def test_axis_descendant_or_self(self):
        self.tokens('///').are([
            ('axis', '///')
        ])

    def test_axis_ancestor_or_self(self):
        self.tokens('/ancestor-or-self::').are([
            ('axis', '/ancestor-or-self::')
        ])

    def test_axis_ancestor(self):
        self.tokens('/ancestor::').are([
            ('axis', '/ancestor::')
        ])

    def test_quoted_search_term(self):
        self.tokens('"//and*=>"').are([
            ('search term', '//and*=>')
        ])

    def test_expression(self):
        self.tokens('@text = test').are([
            ('attribute', 'text'),
            ('operator', '='),
            ('search term', 'test'),
        ])

    def test_parenthesis(self):
        self.tokens('()').are([
            ('punctuation', '('),
            ('punctuation', ')'),
        ])

if __name__ == '__main__':
    unittest.main()
