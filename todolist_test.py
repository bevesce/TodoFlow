import unittest
from todolist import Token, Lexer, Parser, TodoList
from filterpredicate import predicate

def line_type(line):
    return Token(line).type


class TokenTest(unittest.TestCase):
    def test_token_type(self):
        self.assertEqual(line_type("ds  - abs"), 'note')

        self.assertEqual(line_type("- abs"), 'task')
        self.assertEqual(line_type("- abs:"), 'task')
        self.assertEqual(line_type("- abs: @done"), 'task')

        self.assertEqual(line_type("abs:"), 'project-title')
        self.assertEqual(line_type("abs: @done @today @next"), 'project-title')

        self.assertEqual(line_type("abs: "), 'note')
        self.assertEqual(line_type("abs: @done 2"), 'note')
        self.assertEqual(line_type("abs: @done "), 'note')
        self.assertEqual(line_type("abs: "), 'note')

    def test_todolist_parse(self):
        l = Lexer(
"""
- 1 @due(2013-02-13)
- 1 @due(2013-01-13) @done
- 43 @doner

""".split('\n'))
        t = Parser(l).parse()
        print t.as_alfred_xml()
# run
unittest.main()
