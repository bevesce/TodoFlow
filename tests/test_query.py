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
        self.query = '\n\nq:' + query
        self.filtered = self.todos.filter(query)
        return self

    def gives(self, text):
        self.assertEqual(str(self.filtered).strip(), text.strip(), self.query)

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

    def test_014(self):
        self.filtering("""
- r 0
- q 1
- r 1
- q 2
\t- r 3
\t- r 4
- r 5
""").by('r[0:3]').gives("""
- r 0
- r 1
- q 2
\t- r 3
""")

    def test_015(self):
        self.filtering("""
d:
\ta @q
\tc
\tb @q
\td
dd:
\ta
\tx @q
""").by('/d/@q[0]').gives("""
d:
\ta @q
dd:
\tx @q
""")

    def test_016(self):
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

    def test_017(self):
        self.filtering("""
Inbox:
\tR:
\tT:
Test
""").by('/*').gives("""
Inbox:
Test
""")

    def test_018(self):
        self.filtering("""
r
\tw
\tq
\tw
\t\tr
\t\tq
\tq
\t\tr
\t\t\tw
""").by('r/w').gives("""
r
\tw
\tw
\tq
\t\tr
\t\t\tw
""")

    def test_019(self):
        self.filtering("""
r
\tq
\t\tw
\tq
w
""").by('r//w').gives("""
r
\tq
\t\tw
""")

    def test_020(self):
        self.filtering("""
r
\tq
\t\tw
\tq
w
""").by('r///w').gives("""
r
\tq
\t\tw
""")

    def test_021(self):
        self.filtering("""
r
\tq 1
\tq 2
r
\tq 3
\tq 4
""").by('r/q[0]').gives("""
r
\tq 1
r
\tq 3
""")

    def test_022(self):
        self.filtering("""
r
r @d
""").by('r except @d').gives("""
r
""")

    def test_023(self):
        self.filtering("""
r
r @d
q @d
""").by('r intersect @d').gives("""
r @d
""")

#     def test_024(self):
#         self.filtering("""
# w
# \t\tq
# \t\t\tr
# \t\tq
# \tw
# """).by('/ancestor-or-self::r').gives("""
# w
# \tr
# \t\tq
# \t\t\tr
# """)

if __name__ == '__main__':
    unittest.main()
