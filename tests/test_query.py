from __future__ import unicode_literals

import unittest
import datetime as dt

from todoflow.query_parser import parse
from todoflow import Todos


class TestQuery(unittest.TestCase):
    def filtering(self, text):
        self.todos = Todos(text)
        return self

    def by(self, query):
        self.filtered = self.todos.filter(query)
        return self

    def gives(self, text):
        self.assertEqual(str(self.filtered).strip(), text.strip())

    def test_001(self):
        self.filtering("""
- r
- q
""").by('r').gives("""
- r
""")

    def test_002(self):
                self.filtering("""
- r
- q
- w
""").by('r or w').gives("""
- r
- w
""")

    def test_003(self):
                self.filtering("""
- r @a(1)
- q @a(@)
- w @a
""").by('@a = 1').gives("""
- r @a(1)
""")

    def test_004(self):
                self.filtering("""
Inbox:
\t- q @a(@)
\t- w @a
Test:
""").by('project Inbox').gives("""
Inbox:
""")


    def test_005(self):
        self.filtering("""
Inbox:
\t- q @a(@)
\t- w @a
Test:
""").by('project *').gives("""
Inbox:
Test:
""")

    def test_006(self):
        self.filtering("""
Inbox:
\tR:
\tT:
Test:
""").by('/project *').gives("""
Inbox:
Test:
""")


if __name__ == '__main__':
    unittest.main()
