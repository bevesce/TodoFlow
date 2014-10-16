# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import absolute_import

import unittest
from unittest_extensions import SeriesTestCase

from todoflow.querying.parser import parse as parse_query
from todoflow.parser import parse as parse_todos

import todoflow.querying.query as q
import resources.lists_to_test as lt


class TestSingleQueries(SeriesTestCase):
    def assertQueryTrue(self, query, text):
        self.assertTrue(self.parse_query(query).matches_text(text))

    def assertQueryFalse(self, query, text):
        self.assertFalse(self.parse_query(query).matches_text(text))

    def assertSubstringQueryTrue(self, query, text):
        self.assertTrue(q.SubstringQuery(query).matches_text(text))

    def assertSubstringQueryFalse(self, query, text):
        self.assertFalse(q.SubstringQuery(query).matches_text(text))

    def test_text_predicate(self):
        self.conduct_test_series(
            self.assertSubstringQueryTrue,
            (
                ('word', 'word'),
                ('WORD', 'word'),
                ('word', 'to word to'),
                ('word', 'TO WORD TO'),
                ('word', 'to wordto'),
            )
        )
        self.conduct_test_series(
            self.assertSubstringQueryFalse,
            (
                ('wordd', 'word'),
                ('wordd', 'to word to'),
                ('wordd', 'to wordto'),
                ('WORDD', 'to wordto'),
            )
        )

    def assertNotQueryTrue(self, predicate, text):
        self.assertTrue(q.NotQuery(predicate).matches_text(text))

    def assertNotQueryFalse(self, predicate, text):
        self.assertFalse(q.NotQuery(predicate).matches_text(text))

    def test_not_predicate(self):
        self.conduct_test_series(
            self.assertNotQueryFalse,
            (
                (q.SubstringQuery('word'), 'word'),
                (q.SubstringQuery('word'), 'to word to'),
                (q.SubstringQuery('word'), 'to wordto'),
            )
        )
        self.conduct_test_series(
            self.assertNotQueryTrue,
            (
                (q.SubstringQuery('wordd'), 'word'),
                (q.SubstringQuery('wdord'), 'to word to'),
                (q.SubstringQuery('wordw'), 'to wordto'),
            )
        )

    def test_tag_query(self):
        self.assertTrue(q.TagQuery('@done').matches_text('- ddd @done(2014-10-13) ds'))
        self.assertFalse(q.TagQuery('@don').matches_text('- ddd @done(2014-10-13) ds'))

    def assertBinaryQueryTrue(self, query_contructor, subquery1, subquery2, text):
        self.assertTrue(query_contructor(subquery1, subquery2).matches_text(text))

    def assertBinaryQueryFalse(self, query_contructor, subquery1, subquery2, text):
        self.assertFalse(query_contructor(subquery1, subquery2).matches_text(text))

    def test_and_query(self):
        q1 = q.SubstringQuery('a')
        q2 = q.SubstringQuery('b')
        self.assertBinaryQueryTrue(q.AndQuery, q1, q2, 'ab')
        self.assertBinaryQueryFalse(q.AndQuery, q1, q2, 'aa')
        self.assertBinaryQueryFalse(q.AndQuery, q1, q2, 'bb')
        self.assertBinaryQueryFalse(q.AndQuery, q1, q2, 'cc')

    def test_or_query(self):
        q1 = q.SubstringQuery('a')
        q2 = q.SubstringQuery('b')
        self.assertBinaryQueryTrue(q.OrQuery, q1, q2, 'ab')
        self.assertBinaryQueryTrue(q.OrQuery, q1, q2, 'aa')
        self.assertBinaryQueryTrue(q.OrQuery, q1, q2, 'bb')
        self.assertBinaryQueryFalse(q.OrQuery, q1, q2, 'cc')

    def assertTagOpQueryTrue(self, tag, op, right_side, text):
        self.assertTrue(q.TagOpQuery(tag, op, right_side).matches_text(text))

    def assertTagOpQueryFalse(self, tag, op, right_side, text):
        self.assertFalse(q.TagOpQuery(tag, op, right_side).matches_text(text))

    def test_tag_op_query(self):
        tag = '@d'
        self.conduct_test_series(
            self.assertTagOpQueryTrue,
            (
                ('@d', lambda l, r: l == r, 'x', 'fd f @d(x) fd'),
                ('@d', lambda l, r: l < r, '3', 'fd f @d(1) fd'),
                ('@d', lambda l, r: l != r, '3', 'fd f @d(1) fd'),
                ('@d', lambda l, r: l < r, 'x', 'ds @d()'),
            )
        )
        self.assertTagOpQueryFalse('@d', lambda l, r: l > r, 'x', 'ds')
        self.assertTagOpQueryFalse('@d', lambda l, r: l < r, 'x', 'ds')


class TestParsing(SeriesTestCase):
    def assertQueryType(self, query_text, query_type):
        self.assertTrue(isinstance(parse_query(query_text), query_type))

    def test_parsing(self):
        self.conduct_test_series(
            self.assertQueryType,
            (
                ('abc', q.SubstringQuery),
                ('abc def ghi', q.SubstringQuery),
                ('abc and def', q.AndQuery),
                ('abc and def and ghi', q.AndQuery),
                ('(abc and def) and ghi', q.AndQuery),
                ('(abc or def) and ghi', q.AndQuery),
                ('(abc or def) or ghi', q.OrQuery),
                ('abc and def or ghi', q.AndQuery),
                ('abc or def', q.OrQuery),
                ('not def', q.NotQuery),
                ('@d', q.TagQuery),
                ('@d and abc', q.AndQuery),
                ('@d = 1', q.TagOpQuery),
                ('@d != 1', q.TagOpQuery),
                ('@d <= 1', q.TagOpQuery),
                ('@d >= 1', q.TagOpQuery),
                ('@d ≠ 1', q.TagOpQuery),
                ('@d ≤ 1', q.TagOpQuery),
                ('@d ≥ 1', q.TagOpQuery),
                ('@d < 1', q.TagOpQuery),
                ('@d > 1', q.TagOpQuery),
                ('@d -> 1', q.TagOpQuery),
                ('@d <- 1', q.TagOpQuery),
                ('@d ∋ 1', q.TagOpQuery),
                ('@d ∈ 1', q.TagOpQuery),
                ('@d <- 1 +d', q.PlusDescendants),
            )
        )
        query = parse_query('(a and b) and (c or d)')
        self.assertTrue(isinstance(query, q.AndQuery))
        self.assertTrue(isinstance(query.query1, q.AndQuery))
        self.assertTrue(isinstance(query.query2, q.OrQuery))
        query = parse_query('(a +d) and x')
        self.assertTrue(isinstance(query.query1, q.PlusDescendants))


class TestSearching(SeriesTestCase):
    def assertSearchResults(self, todos, query, result):
        self.assertEqual(
            [t.__str__() for t in parse_todos(todos).search(parse_query(query))],
            result
        )

    def test_substring(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x y', 'x', ['x y']),
                ('x y\nx', 'x', ['x y', 'x']),
                ('x y\n  x', 'x', ['x y', '  x']),
                ('x y\n  x', 'y', ['x y']),
                ('x y\n  x', 'z', []),
            )
        )

    def test_tag(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x @y', '@y', ['x @y']),
                ('@x y\n@x', '@x', ['@x y', '@x']),
                ('@x y\n  @x', '@x', ['@x y', '  @x']),
                ('@x y\n  @x', '@z', []),
            )
        )

    def test_tag_op(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x @y(1)', '@y = 1', ['x @y(1)']),
                ('- x @y(1)', '@y >= 1', ['- x @y(1)']),
                ('- x @y(1)', '@y > 1', []),
                ('x @x', '@y <= 1', []),
                ('x @x(1)', '@y <= 1', []),
            )
        )

    def test_not(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('- x y', 'not x', []),
                ('x y\n- z y', 'not z', ['x y']),
            )
        )

    def test_and(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x y', 'x and y', ['x y']),
                ('x', 'x and y', []),
                ('y', 'x and y', []),
                ('z', 'x and y', []),
            )
        )

    def test_and(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x y', 'x or y', ['x y']),
                ('x', 'x or y', ['x']),
                ('y', 'x or y', ['y']),
                ('z', 'x or y', []),
            )
        )

    def test_project(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x:\n y', ': = x', ['x:', ' y']),
                ('x:\n y\n  z', ': =  x', ['x:', ' y', '  z']),
                ('x:\n y', ': != x', []),
            )
        )

    def test_plus_descendants(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x:\n y', 'x +d', ['x:', ' y']),
                ('x:\n y\n  z', 'x +d', ['x:', ' y', '  z']),
            )
        )

    def test_only_first(self):
        self.conduct_test_series(
            self.assertSearchResults,
            (
                ('x:\n y @d\n z @d\n w', '@d +f', [' y @d']),
                ('x:\n y @d\n z\n w', 'not @d +f', ['x:', ' z']),
            )
        )

    def test_type(self):
        text = 'p:\n - t\nn\n- t'
        self.conduct_test_series(
            self.assertSearchResults,
            (
                (text, 'type = task', [' - t', '- t']),
                (text, 'type = "project"', ['p:']),
                (text, 'type = note', ['n']),
                (text, 'type = "note"', ['n']),
            )
        )

    def test_unique_id(self):
        text = 'p:\n - x\nn\n- y'
        todos = parse_todos(text)
        item = todos.get_item('x')
        self.assertEqual(
            item,
            todos.get_item('uniqueid = ' + item.uniqueid)
        )


class TestFilter(SeriesTestCase):
    def assertFilterResult(self, todos, query, result):
        self.assertEqual(
            parse_todos(todos).filter(parse_query(query)).__str__(),
            result
        )

    def test_filtering(self):
        self.assertFilterResult('x @d', '@d', 'x @d')
        self.assertFilterResult('x @d\ny', '@d', 'x @d')
        self.assertFilterResult(lt.f1, lt.word_x, lt.f1__word_x)

    def test_unicode_handling(self):
        todos_text = '- @d'
        todos = parse_todos(todos_text)
        self.assertEqual(todos_text, str(todos.filter('@d')))

if __name__ == '__main__':
    unittest.main()
