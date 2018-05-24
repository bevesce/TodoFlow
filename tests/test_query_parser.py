from __future__ import unicode_literals

import unittest
import datetime as dt

from todoflow.query_parser import QueryParser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def parsing(self, text):
        self.parsed = self.parser.parse(text)
        return self

    def gives(self, text):
        self.assertEqual(str(self.parsed), text)

    def test_001(self):
        self.parsing('r union w').gives(
            '(<S> (<L>(<R> @text contains [i] r </R>) [:]</L>) union (<L>(<R> @text contains [i] w </R>) [:]</L>) </S>)'
        )

    def test_002(self):
        self.parsing('@tag').gives('(<L>tag [:]</L>)')

    def test_003(self):
        self.parsing('project *').gives(
            '(<L>(<B> (<R> @type = [i] project </R>) and * </B>) [:]</L>)'
        )

    def test_004(self):
        self.parsing('t/w').gives(
            '(<I> (<L>(<R> @text contains [i] t </R>) [:]</L>) / (<L>(<R> @text contains [i] w </R>) [:]</L>) </I>)'
        )

    def test_005(self):
        self.parsing('r union w union q').gives(
            '(<S> (<S> (<L>(<R> @text contains [i] r </R>) [:]</L>) union (<L>(<R> @text contains [i] w </R>) [:]</L>) </S>) union (<L>(<R> @text contains [i] q </R>) [:]</L>) </S>)'
        )

    def test_006(self):
        self.parsing('r union w intersect q').gives(
            '(<S> (<S> (<L>(<R> @text contains [i] r </R>) [:]</L>) union (<L>(<R> @text contains [i] w </R>) [:]</L>) </S>) intersect (<L>(<R> @text contains [i] q </R>) [:]</L>) </S>)'
        )

    def test_007(self):
        self.parsing('/t').gives('(<I>  / (<L>(<R> @text contains [i] t </R>) [:]</L>) </I>)')

    def test_008(self):
        self.parsing('t[0]').gives('(<L>(<R> @text contains [i] t </R>) [0]</L>)')

    def test_009(self):
        self.parsing('t[42]/w[1:2]').gives(
            '(<I> (<L>(<R> @text contains [i] t </R>) [42]</L>) / (<L>(<R> @text contains [i] w </R>) [1:2]</L>) </I>)'
        )

    def test_010(self):
        self.parsing('r[0] union w[1]').gives(
            '(<S> (<L>(<R> @text contains [i] r </R>) [0]</L>) union (<L>(<R> @text contains [i] w </R>) [1]</L>) </S>)'
        )

    def test_011(self):
        self.parsing('/my heading[0]').gives(
            '(<I>  / (<L>(<R> @text contains [i] my heading </R>) [0]</L>) </I>)'
        )

    def test_012(self):
        self.parsing('/my heading').gives(
            '(<I>  / (<L>(<R> @text contains [i] my heading </R>) [:]</L>) </I>)'
        )

    def test_013(self):
        self.parsing('(1 or 2) and 3').gives(
            '(<L>(<B> (<B> (<R> @text contains [i] 1 </R>) or (<R> @text contains [i] 2 </R>) </B>) and (<R> @text contains [i] 3 </R>) </B>) [:]</L>)'
        )

    def test_014(self):
        self.parsing('(1 union 2) intersect 3').gives(
            '(<S> (<L>(<S> (<L>(<R> @text contains [i] 1 </R>) [:]</L>) union (<L>(<R> @text contains [i] 2 </R>) [:]</L>) </S>) [:]</L>) intersect (<L>(<R> @text contains [i] 3 </R>) [:]</L>) </S>)'
        )

    def test_015(self):
        self.parsing('(project Inbox//* union //@today) except //@done').gives(
            '(<S> (<L>(<S> (<I> (<L>(<B> (<R> @type = [i] project </R>) and (<R> @text contains [i] Inbox </R>) </B>) [:]</L>) // (<L>* [:]</L>) </I>) union (<I>  // (<L>today [:]</L>) </I>) </S>) [:]</L>) except (<I>  // (<L>done [:]</L>) </I>) </S>)'
        )

    def test_016(self):
        self.parsing('not @today').gives(
            '(<L>(<U> not today </U>) [:]</L>)'
        )

    def test_017(self):
        self.parsing('not q and w').gives(
            '(<L>(<B> (<U> not (<R> @text contains [i] q </R>) </U>) and (<R> @text contains [i] w </R>) </B>) [:]</L>)'
        )

    def test_018(self):
        self.parsing('not (q and w)').gives(
            '(<L>(<U> not (<B> (<R> @text contains [i] q </R>) and (<R> @text contains [i] w </R>) </B>) </U>) [:]</L>)'
        )

    def test_019(self):
        self.parsing('(one or two) and not three').gives(
            '(<L>(<B> (<B> (<R> @text contains [i] one </R>) or (<R> @text contains [i] two </R>) </B>) and (<U> not (<R> @text contains [i] three </R>) </U>) </B>) [:]</L>)'
        )

    def test_020(self):
        self.parsing('(project *//not @done)[0]').gives(
            '(<L>(<I> (<L>(<B> (<R> @type = [i] project </R>) and * </B>) [:]</L>) // (<L>(<U> not done </U>) [:]</L>) </I>) [0]</L>)'
        )

    def test_021(self):
        self.parsing('(project Inbox//* union //@today) except //@done').gives(
            '(<S> (<L>(<S> (<I> (<L>(<B> (<R> @type = [i] project </R>) and (<R> @text contains [i] Inbox </R>) </B>) [:]</L>) // (<L>* [:]</L>) </I>) union (<I>  // (<L>today [:]</L>) </I>) </S>) [:]</L>) except (<I>  // (<L>done [:]</L>) </I>) </S>)'
        )

    def test_022(self):
        self.parsing('@tag and @test').gives('(<L>(<B> tag and test </B>) [:]</L>)')

    def test_023(self):
        self.parsing('t/w/q').gives(
            '(<I> (<I> (<L>(<R> @text contains [i] t </R>) [:]</L>) / (<L>(<R> @text contains [i] w </R>) [:]</L>) </I>) / (<L>(<R> @text contains [i] q </R>) [:]</L>) </I>)'
        )

    def test_024(self):
        self.parsing('/d/@q[0]').gives(
            '(<I> (<I>  / (<L>(<R> @text contains [i] d </R>) [:]</L>) </I>) / (<L>q [0]</L>) </I>)'
        )

    def test_025(self):
        self.parsing('not (@done or @waiting)').gives(
            '(<L>(<U> not (<B> done or waiting </B>) </U>) [:]</L>)'
        )

    def test_026(self):
        self.parsing('@today and not (@done or @waiting)').gives(
            '(<L>(<B> today and (<U> not (<B> done or waiting </B>) </U>) </B>) [:]</L>)'
        )

    def test_026(self):
        self.parsing('@today and not @done)').gives(
            '(<L>(<B> today and (<U> not done </U>) </B>) [:]</L>)'
        )


if __name__ == '__main__':
    unittest.main()
