from __future__ import unicode_literals

import unittest

import todoflow.textutils as tu


class TestTypeCheckers(unittest.TestCase):
    def setUp(self):
        self.task = '- task'
        self.indented_task = '\t\t- task'
        self.project = '  Project:'
        self.sequential_project = '  Project::'
        self.note = 'note'

    def test_is_task(self):
        self.assertTrue(tu.is_task(self.task))
        self.assertTrue(tu.is_task(self.indented_task))
        self.assertFalse(tu.is_task(self.project))
        self.assertFalse(tu.is_task(self.note))

    def test_is_project(self):
        self.assertFalse(tu.is_project(self.task))
        self.assertFalse(tu.is_project(self.indented_task))
        self.assertTrue(tu.is_project(self.project))
        self.assertTrue(tu.is_project(self.sequential_project))
        self.assertFalse(tu.is_project(self.note))

    def test_is_note(self):
        self.assertFalse(tu.is_note(self.task))
        self.assertFalse(tu.is_note(self.indented_task))
        self.assertFalse(tu.is_note(self.project))
        self.assertTrue(tu.is_note(self.note))


class TestTagsFunctions(unittest.TestCase):
    def test_has_tag(self):
        self.assertTrue(tu.has_tag('- to @tag', 'tag'))
        self.assertTrue(tu.has_tag('- to @tag', '@tag'))
        self.assertFalse(tu.has_tag('- to @tag2', '@tag'))
        self.assertFalse(tu.has_tag('- to @tag2', 'tag'))
        self.assertFalse(tu.has_tag('- to@tag2', 'tag2'))
        self.assertTrue(tu.has_tag('- @tag2', 'tag2'))
        self.assertTrue(tu.has_tag('@tag2', 'tag2'))
        self.assertTrue(tu.has_tag('@tag(2) ds', 'tag'))
        self.assertTrue(tu.has_tag('@tag(2)', 'tag'))
        self.assertTrue(tu.has_tag('@ta*g2', 'ta*g2'))

    def test_create_tag_pattern(self):
        p1 = tu._create_tag_pattern('tag')
        self.assertTrue(p1.match('@tag'))
        self.assertTrue(p1.match('@tag(2)'))
        self.assertTrue(p1.findall('@tag(2)'))
        self.assertTrue(p1.findall('ewq @tag(2)'))
        self.assertTrue(p1.findall('ewq @tag(2) fds'))
        self.assertFalse(p1.findall('ewq@tag(2) fds'))
        self.assertFalse(p1.findall('ewq @tag(2)fds'))
        self.assertFalse(p1.findall('ewq @tagfds'))
        p2 = tu._create_tag_pattern('ta+*/g')
        self.assertTrue(p2.match('@ta+*/g'))
        p3 = tu._create_tag_pattern('@ta+*/g')
        self.assertTrue(p3.match('@ta+*/g'))

    def test_fix_tag(self):
        self.assertEqual('@t', tu._fix_tag('t'))
        self.assertEqual('@t', tu._fix_tag('@t'))

    def test_get_tag_param(self):
        self.assertEqual('2', tu.get_tag_param('@t(2)', 't'))
        self.assertEqual('2', tu.get_tag_param('@t(2)', '@t'))
        self.assertEqual('', tu.get_tag_param('@t()', 't'))
        self.assertEqual(None, tu.get_tag_param('@t', 't'))
        self.assertEqual(None, tu.get_tag_param('@k', 't'))
        self.assertEqual(None, tu.get_tag_param('yo @t d', '@t'))

    def test_remove_tag(self):
        self.assertEqual('yo yo', tu.remove_tag('yo @t yo', 't'))
        self.assertEqual('yo yo', tu.remove_tag('yo @t yo', '@t'))
        self.assertEqual('yo yo', tu.remove_tag('yo @t(22) yo', '@t'))
        self.assertEqual('yo yo', tu.remove_tag('yo yo @t(22)', '@t'))
        self.assertEqual('yo yo @t2', tu.remove_tag('yo yo @t(22) @t2', '@t'))
        self.assertEqual('yo yo @t2 ', tu.remove_tag('yo yo @t(22) @t2 ', '@t'))

    def test_prepare_param(self):
        self.assertEqual('()', tu._prepare_param(''))
        self.assertEqual('(d)', tu._prepare_param('d'))
        self.assertEqual('(d )', tu._prepare_param('d '))
        self.assertEqual('(2)', tu._prepare_param(2))
        self.assertEqual('(0)', tu._prepare_param(0))

    def test_prepare_text_for_tag(self):
        self.assertEqual('t ', tu._prepare_text_for_tag('t'))
        self.assertEqual('t ', tu._prepare_text_for_tag('t '))

    def test_replace_tag(self):
        self.assertEqual('d k fd', tu.replace_tag('d @t fd', 't', 'k'))
        self.assertEqual('d @k fd', tu.replace_tag('d @k fd', 't', 'k'))
        self.assertEqual('d k', tu.replace_tag('d @t', 't', 'k'))
        self.assertEqual('d @k d', tu.replace_tag('d @t d', '@t', '@k'))

    def test_add_tag(self):
        self.assertEqual('yo @done', tu.add_tag('yo', 'done'))
        self.assertEqual('yo @done', tu.add_tag('yo', '@done'))
        self.assertEqual('yo @done(2)', tu.add_tag('yo', '@done', 2))
        self.assertEqual('yo @done(2) yo', tu.add_tag('yo @done yo', '@done', 2))
        self.assertEqual('yo @done(2) yo', tu.add_tag('yo @done(1) yo', '@done', 2))
        self.assertEqual('yo @done(0) yo', tu.add_tag('yo @done(1) yo', '@done', 0))

    def test_enclose_tag(self):
        self.assertEqual('yo **@t**', tu.enclode_tag('yo @t', '@t', '**'))
        self.assertEqual('yo **@t** d', tu.enclode_tag('yo @t d', '@t', '**'))
        self.assertEqual('yo <tag>@t</tag>', tu.enclode_tag('yo @t', '@t', '<tag>', '</tag>'))

    def test_get_all_tags(self):
        self.assertEqual(['t', 'k'], tu.get_all_tags('yo @t dfd @k'))
        self.assertEqual(['t', 'k'], tu.get_all_tags('yo @t(9) dfd @k'))
        self.assertEqual(['@t', '@k'], tu.get_all_tags('yo @t(9) dfd @k', include_indicator=True))
        self.assertEqual(['t', 'k'], tu.get_all_tags('yo @t(9) dfd @k(fd)'))

    def test_increase_tag_param(self):
        self.assertEqual('yo @t(2)', tu.modify_tag_param('yo @t(1)', 't', lambda p: int(p) + 1))
        self.assertEqual('yo @t(1)', tu.modify_tag_param('yo @t(0)', '@t', lambda p: int(p) + 1))
        self.assertEqual('yo @t(0)', tu.modify_tag_param('yo @t(-1)', 't', lambda p: int(p) + 1))

    def test_sort_by_tag(self):
        from random import shuffle
        texts_collection = ['yo', 'yo @t(1)', '@t(2) @k(1000)', 'fd @t(4)']
        shuffled_texts_collection = list(texts_collection)
        shuffle(shuffled_texts_collection)
        self.assertEqual(
            texts_collection,
            tu.sort_by_tag_param(shuffled_texts_collection, 't')
        )
        self.assertEqual(
            texts_collection[::-1],
            tu.sort_by_tag_param(shuffled_texts_collection, 't', reverse=True)
        )


class TestFormatters(unittest.TestCase):
    def test_strip_formatting(self):
        self.assertEqual('yo', tu.strip_formatting('\t\t- yo'))
        self.assertEqual('yo:', tu.strip_formatting('\t\t- yo:'))
        self.assertEqual('yo', tu.strip_formatting('\t\tyo:'))
        self.assertEqual('yo', tu.strip_formatting('yo'))

    def test_strip_formatting_and_tags(self):
        self.assertEqual('yo d', tu.strip_formatting_and_tags('\t\t- yo @to(2) d @t'))
        self.assertEqual('yo d', tu.strip_formatting_and_tags('\t\t- yo @to(2) d @t:'))

    def test_calculate_indent_level(self):
        self.assertEqual(0, tu.calculate_indent_level('t'))
        self.assertEqual(1, tu.calculate_indent_level(' t'))
        self.assertEqual(2, tu.calculate_indent_level('  t'))
        self.assertEqual(4, tu.calculate_indent_level('\tt'))
        self.assertEqual(4, tu.calculate_indent_level('    t'))
        self.assertEqual(8, tu.calculate_indent_level('\t\tt'))
        self.assertEqual(8, tu.calculate_indent_level('        t'))
        self.assertEqual(8, tu.calculate_indent_level('        t    '))
        self.assertEqual(8, tu.calculate_indent_level('    \tt    '))
        self.assertEqual(8, tu.calculate_indent_level('\t    t    '))
        self.assertEqual(10, tu.calculate_indent_level('\t      t    '))


if __name__ == '__main__':
    unittest.main()
