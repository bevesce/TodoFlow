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
""").by('/*').gives("""
Inbox:
Test:
""")

    def test_007(self):
        self.filtering("""
Inbox:
\tR:
\tT:
Test
""").by('/project *').gives("""
Inbox:""")


    def test_007(self):
        self.filtering("""
Inbox:
\tR:
\tT:
Test
""").by('//*').gives("""
Inbox:
\tR:
\tT:
Test
""")

    def test_008(self):
        self.filtering("""
r 0
r 1
r 2
r 3
""").by('r[0]').gives("""
r 0
""")

    def test_009(self):
        self.filtering("""
r 0
r 1
r 2
r 3
""").by('r[1]').gives("""
r 1
""")

    def test_010(self):
        self.filtering("""
r
\tq
\tw
e
\tq
\tw
""").by('r/w').gives("""
r
\tw
""")

    def test_011(self):
        self.filtering("""
r
\tq
\tw
\tw
\t\tl
\tw
\t\tp
e
\tq
\tw
""").by('r/w/p').gives("""
r
\tw
\t\tp
""")

    def test_012(self):
        self.filtering("""
d @due(2016-10-03)
d @due(2016-10-04)
d @due(2016-10-05)
""").by('@due =[d] 2016-10-04').gives("""
d @due(2016-10-04)
""")

    def test_013(self):
        self.filtering("""
r
\tq
\tw
\tw
\t\tl
\tw
\t\tp
\tt
\t\tt
e
\tq
\tw
""").by('r/w/p union t/t').gives("""
r
\tw
\t\tp
\tt
\t\tt
""")

if __name__ == '__main__':
    unittest.main()
