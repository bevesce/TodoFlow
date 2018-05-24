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

    def test_024(self):
        self.filtering("""
w
\tr
\t\tr
\t\tb
\tq
\t\tr
\t\ta
""").by('w//*/ancestor-or-self::r').gives("""
w
\tr
\t\tr
\tq
\t\tr
""")

    def test_025(self):
        self.filtering("""
w
\tq
\tr
\t\tx
\t\t\ty
\tq
\t\tx
""").by('w//y/ancestor::r').gives("""
w
\tr
""")

    def test_026(self):
        self.filtering("""
w
\tq
\tr
\t\tq
""").by('w//q/parent::r').gives("""
w
\tr
""")

    def test_027(self):
        self.filtering("""
w
q
r 1
x
r 2
""").by('w/following-sibling::r').gives("""
r 1
r 2
""")

    def test_028(self):
        self.filtering("""
r 0
x
\tw
\t\tr 1
\tr 2
q
r 3
q
""").by('w/following::r').gives("""
x
\tw
\t\tr 1
\tr 2
r 3
""")

    def test_029(self):
        self.filtering("""
r 1
q
r 2
w
""").by('w/preceding-sibling::r').gives("""
r 1
r 2
""")

    def test_030(self):
        self.filtering("""
r 0
x
\tr 1
\t\tq
\t\tr 2
\t\tw
x
\ty
""").by('w/preceding::r').gives("""
r 0
x
\tr 1
\t\tr 2
""")

    def test_031(self):
        self.filtering("""
r
q
\tr
""").by('/ancestor-or-self::r').gives("""
""")

    def test_032(self):
        self.filtering("""
r 1
q
\tr
r 2
\tq
""").by('/ancestor::r').gives("""
""")

    def test_033(self):
        self.filtering("""
r 1
q
\tr 2
r 3
\t q
q
\tr 4
\t\tq
\tw
""").by('/parent::r').gives("""
""")

    def test_034(self):
        self.filtering("""
r 1
q
r 2
w
\tq
\tr 3
""").by('/following-sibling::r').gives("""
""")

    def test_035(self):
        self.filtering("""
q
r 1
w
\tq
\tr 2
""").by('/following::r').gives("""
r 1
w
\tr 2
""")

    def test_036(self):
        self.filtering("""
q
r 1
w
\tq
\tr 2
\tq
e
\tq
\tr 3
""").by('/preceding-sibling::r').gives("""
""")

    def test_037(self):
        self.filtering("""
r 1
w
\tr 2
\tq
e
\tr 4
""").by('/preceding::r').gives("""
""")

    def test_038(self):
        self.filtering("""
todo:
\tp
to:
\tto
\tto
\tko:
""").by('project *').gives("""
todo:
to:
\tko:
""")

    def test_038b(self):
        items = list(Todos("""todo:
\tp
to:
\tto
\tto
\tko:
""").search('project *'))
        self.assertEqual([i.get_text() for i in items], ['todo:', 'to:', '\tko:'])

    def test_039(self):
        self.filtering("""
1 @working
2 @workign @done
3 @done
""").by('@working and not @done').gives("""
1 @working
""")

    def test_039(self):
        self.filtering("""
test @p(eric)
test @p(john,graham)
test @p(graham,eric)
""").by('@p contains[l] john').gives("""
test @p(john,graham)
""")

    def test_039s(self):
        self.filtering("""
test @p(john,graham)
test @p(John,graham)
""").by('@p contains[sl] John').gives("""
test @p(John,graham)
""")


if __name__ == '__main__':
    unittest.main()
