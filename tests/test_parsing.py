from __future__ import unicode_literals

import unittest

from unittest_extensions import SeriesTestCase

import todoflow.lexer as lexer
import todoflow.parser as parser
import resources.lists_to_test as lt
import todoflow.config


class TestLexer(SeriesTestCase):
    def test_lexer_initiation(self):
        lex = lexer.Lexer('test\nto')
        self.assertTrue(lex)
        self.assertEqual(2, len(lex.lines))

    def test_lexer_indentation_handling(self):
        def assertTokensLen(length, text):
            self.assertEqual(length, len(lexer.Lexer(text).tokens))
        self.conduct_test_series(
            assertTokensLen,
            (
                (1 + 0, lt.tokens0),
                (1 + 1, lt.tokens1),
                (1 + 2, lt.tokens2),
                (1 + 3 + 1, lt.tokens3),
                (1 + 4 + 1, lt.tokens4),
                (1 + 5 + 1, lt.tokens5),
                (1 + 6 + 1, lt.tokens6),
                (1 + 7 + 1, lt.tokens7),
                (1 + 8 + 1, lt.tokens8),
                (1 + 9, lt.tokens9.strip()),
                (1 + 9 + 1, lt.tokens9),
            )
        )

    def test_lexer(self):
        def assertTokensEqual(expected, text):
            tokens_repesentation = ''.join([t.tok() for t in lexer.Lexer(text).tokens])
            self.assertEqual(expected, tokens_repesentation)
        self.conduct_test_series(
            assertTokensEqual,
            (
                ('*$', lt.tokens1),
                ('**$', lt.tokens2),
                ('*>*n$', lt.tokens3),
                ('*>**n$', lt.tokens4),
                ('*>*>*n$', lt.tokens5),
                ('*>*>**n$', lt.tokens6),
                ('*>*>*>*n$', lt.tokens7),
                ('*>*>*<<*n$', lt.tokens8),
                ('*>*n>*<<*n$', lt.tokens9),
                ('*>*nn>*<<*n$', lt.tokens10),
                ('*>*nn>*<<*$', lt.tokens10.strip()),
                ('*>*nn>*n<<*n$', lt.tokens11),
                ('*>*nn>*n<<*$', lt.tokens11.strip()),
            )
        )

    def test_token_types(self):
        text = lexer.TextToken('')
        self.assertTrue(text.is_text)
        self.assertFalse(text.is_newline)
        newline = lexer.NewlineToken()
        self.assertTrue(newline.is_newline)
        self.assertFalse(newline.is_text)
        indent = lexer.IndentToken()
        self.assertTrue(indent.is_indent)
        dedent = lexer.DedentToken()
        self.assertTrue(dedent.is_dedent)
        end = lexer.EndToken()
        self.assertTrue(end.is_end)
        self.assertFalse(end.is_text)


class TestParser(SeriesTestCase):
    def test_parser_init(self):
        parsers_instance = parser.Parser()
        parsers_instance.parse('')

    def test_main_list_length(self):
        def assertItemsLength(length, text):
            todolist = parser.parse(text)
            self.assertEqual(length, len(todolist))
        self.conduct_test_series(
            assertItemsLength,
            (
                (1, lt.tokens1),
                (2, lt.tokens2),
                (2, lt.tokens3),
                (1, lt.tokens4.strip()),
                (2, lt.tokens4),
                (2, lt.tokens5),
                (3, lt.tokens8),
                (3, lt.tokens10),
                (4, lt.tokens11),
                (3, lt.tokens11.strip()),
            )
        )

    def test_first_sublist_length(self):
        def assertSublistLength(length, text):
            todolist = parser.parse(text)
            self.assertEqual(length, len(todolist.items[0].subtodos))
        self.conduct_test_series(
            assertSublistLength,
            (
                (0, lt.tokens1),
                (1, lt.tokens3),
                (2, lt.tokens4),
                (1, lt.tokens9),
            )
        )

    def test_item_types(self):
        def assertItemTypes(types, text):
            todolist = parser.parse(text)
            self.assertEqual(types, todolist._class_repr())
        self.conduct_test_series(
            assertItemTypes,
            (
                (lt.t1_expected, lt.t1),
                (lt.t2_expected, lt.t2),
                (lt.t3_expected, lt.t3),
                (lt.t4_expected, lt.t4),
                (lt.t5_expected, lt.t5),
            )
        )

    def test_parse_to_string(self):
        def assertParseToStringEquals(text):
            self.assertEqual(text, str(parser.parse(text)))
        self.conduct_test_series(
            assertParseToStringEquals,
            (
                ('note', ),
                ('- task', ),
                ('porject:', ),
                ('- task:', ),
                ('- task:\n', ),
                (lt.t1, ),
                (lt.t1_1, ),
                (lt.t2, ),
                (lt.t3, ),
                (lt.t4, ),
                (lt.t5, ),
                (lt.tokens1, ),
                (lt.tokens2, ),
                (lt.tokens3, ),
                (lt.tokens4, ),
                (lt.tokens5, ),
                (lt.tokens6, ),
                (lt.tokens7, ),
                (lt.tokens8, ),
                (lt.tokens9, ),
                (lt.tokens10, ),
                (lt.tokens11, ),
            )
        )


if __name__ == '__main__':
    unittest.main()
