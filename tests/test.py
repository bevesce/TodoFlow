"""Run from directory that contains this file"""

from __future__ import absolute_import
import unittest
import sys
import os.path
import topy as tp
from topy.src.todolist import Task, Note, Project
from topy.src.filterpredicate import parse_predicate
import topy.src.todolist_utils as tu

class TestUtils(unittest.TestCase):
    def test_add_tag(self):
        self.assertEqual('abc @done', tu.add_tag_to_text('abc', 'done'))
        self.assertEqual('abc @done(1)', tu.add_tag_to_text('abc', 'done', 1))
        self.assertEqual('\tabc @done(1)', tu.add_tag_to_text('\tabc ', 'done', 1))

    def test_get_tag_param(self):
        self.assertEqual('1', tu.get_tag_param('abc @done(1)', 'done'))
        self.assertEqual('1', tu.get_tag_param('abc @done(1) fds', 'done'))
        self.assertEqual('1', tu.get_tag_param('@done(1) fds', 'done'))
        self.assertEqual(None, tu.get_tag_param('abc @done', 'done'))

    def test_remove_trailing_tags(self):
        self.assertEqual('abc', tu.remove_trailing_tags('abc @dd @done(1)'))
        self.assertEqual('- abc @kk fds', tu.remove_trailing_tags('- abc @kk fds @done(1) @dd '))  # +
        self.assertEqual('@abc', tu.remove_trailing_tags('@abc'))  # +
        self.assertEqual('abc', tu.remove_trailing_tags('abc'))  # +

    def test_extract_content(self):
        self.assertEqual('abc', tu.extract_content('task', '\t- abc @done @jup'))
        self.assertEqual('abc', tu.extract_content('project', '\tabc: @done @jup'))

    def test_enclose_tags(self):
        self.assertEqual('abc !@done# fds', tu.enclose_tags('abc @done fds', '!', '#'))
        self.assertEqual('abc !@done# ', tu.enclose_tags('abc @done ', '!', '#'))

    def test_remove_tag(self):
        self.assertEqual('abc  fds', tu.remove_tag_from_text('abc @done fds', 'done'))
        self.assertEqual('abc ', tu.remove_tag_from_text('abc @done(fdsf)', 'done'))
        self.assertEqual('abc  fds', tu.remove_tag_from_text('abc @done(fdsf) fds', 'done'))
        self.assertEqual(' abc', tu.remove_tag_from_text('@done(fdsf) abc', 'done'))


class TestsOnItems(unittest.TestCase):
    def _test_item(self, line, query, result=True, constructor=Task):
        item = constructor(line)
        predicate = parse_predicate(query)
        # print item.title.line
        self.assertEqual(
            predicate.test(item),
            result
        )

    def test_words_predicate(self):
        self._test_item('- abc aa a', 'a')
        self._test_item('- abc fds', 'abc')
        self._test_item('- abc fds', 'fds')
        self._test_item('- abc fds', 'abcd', result=False)

    def test_tag_predicate(self):
        self._test_item('- abc @done', '@done')
        self._test_item('@done(2011-11-11) abc', '@done', constructor=Note)
        self._test_item('- abv @done(2011-11-11) fsd', '@done')
        self._test_item('- abv @doner(2011-11-11) fsd', '@done', result=False)

    def test_content(self):
        self._test_item('\t\t- abc', 'content = abc')
        self._test_item('\t\tabc:', 'content = abc', constructor=Project)
        self._test_item('\t\tabc', 'content = abc', constructor=Note)
        self._test_item('\t\tabc', 'content = abcd', constructor=Note, result=False)
        self._test_item('- abc', 'content $ a')
        self._test_item('- abc', 'not content $ d')
        self._test_item('- 123', 'content matches \d\d\d')
        self._test_item('- 123 fd', 'content matches \d+')

    def test_line(self):
        self._test_item('\t\t- abc', 'line =   - abc')
        self._test_item('\t\t- fd abc', 'line $   -')
        self._test_item('\t\tabc: @done', 'line $ :', constructor=Project)
        self._test_item('\t\tfd - abc', 'line $ -', constructor=Note)
        self._test_item('\t\tabc:', 'line = abc:', constructor=Project)
        self._test_item('\t\tabc @done', 'line = "abc @done"', constructor=Note)
        self._test_item('\t\tabc', 'line = abcd', constructor=Note, result=False)
        self._test_item('- abc', 'line $ a')
        self._test_item('- abc', 'not line $ d')

    def test_tag_param(self):
        self._test_item('- d @done(2013-02-23)', '@done < 2013-02-25')
        self._test_item('- d @done(2013-02-23)', '@done > 2013-02-25', result=False)
        self._test_item('- d @done(2013-02-23) fsd', '@done != 2013-02-25')
        self._test_item('- d @done(2013-02-23) fsd', '@done = 2013-02-23')
        self._test_item('- d @done(2013-02-23) fsd', '@done = 2013-02-24', result=False)
        self._test_item('d: @done(zzz)', '@done < a', result=False, constructor=Project)
        self._test_item('d: @done(aaa)', '@done < z', constructor=Project)
        self._test_item('- @done(123)', '@done $ 1')
        self._test_item('- @done(123)', '@done matches \d*')
        self._test_item('- @done', '@done < q', result=False)

    def test_type(self):
        self._test_item('- abc', 'type = task')
        self._test_item('\tabc: @done', 'type = "project"', constructor=Project)
        self._test_item('\tabc @done', 'type = note', constructor=Note)
        self._test_item('\t-abc @done', 'type != note', constructor=Task)
        self._test_item('- abc', 'type < z')

    def test_or_predicate(self):
        self._test_item('- abc', 'a or d')
        self._test_item('- bcd', 'a or d')
        self._test_item('- abc', 'e or d', result=False)

    def test_and_predicate(self):
        self._test_item('- abc d', '(line $ a) and d')
        self._test_item('- bcd', '(line > aaa) and d', result=False)
        self._test_item('- abc', 'e and (type = task)', result=False)

    def test_and_or(self):
        self._test_item('- ac d', '(a or b) and d')
        self._test_item('- ac d', '(a and b) or d')
        self._test_item('- ac d', '(a and b) or g', result=False)

    def test_not_predicate(self):
        self._test_item('- abc', 'not d')
        self._test_item('- bcd', 'not (b and c)', result=False)
        self._test_item('- bcd', 'not b', result=False)


def load_big():
    return tp.from_file('in/big.todo')


class TestsOnFiles(unittest.TestCase):
    def setUp(self):
        self.big = load_big()

    def _test_on_files(self, input_list, out_path, query=''):
        os.path.abspath(out_path)
        if isinstance(input_list, str):
            input_list = tp.from_file(input_list)
        input_list = input_list.filter(query)
        in_txt = input_list.as_plain_text()
        out_txt = open(out_path, 'r').read().strip()
        open('m' + out_path, 'w').write(in_txt)
        # print in_txt
        # print out_txt
        self.assertEqual(in_txt.strip(), out_txt.strip())

    def test_empty(self):
        self._test_on_files('in/empty.todo', 'in/empty.todo')

    def test_one_task(self):
        self._test_on_files('in/one_task.todo', 'in/one_task.todo')

    def test_no_query(self):
        self._test_on_files(self.big, 'in/big.todo')

    def test_index(self):
        self._test_on_files(self.big, 'out/index0.todo', 'index = 0')
        self._test_on_files(self.big, 'out/index2.todo', 'index = 2')

    def test_project(self):
        self._test_on_files(self.big, 'out/ProjectA.todo', 'project = ProjectA')
        self._test_on_files(self.big, 'out/ProjectB.todo', 'project = ProjectB')
        self._test_on_files(self.big, 'out/project-project.todo', 'project $ "project"')
        self._test_on_files(self.big, 'out/notA.todo', 'project != ProjectA')
        self._test_on_files(self.big, 'out/notD.todo', 'not project = ProjectD')

    def test_type(self):
        self._test_on_files(self.big, 'out/only-projects.todo', 'type = "project"')
        self._test_on_files(self.big, 'out/only-tasks.todo', 'type =  task')
        self._test_on_files(self.big, 'out/only-notes.todo', 'type =  note')

    def test_level(self):
        self._test_on_files(self.big, 'out/level0.todo', 'level = 0')
        self._test_on_files(self.big, 'out/level12.todo', 'level < 3')
        self._test_on_files(self.big, 'out/level2up.todo', 'level > 2')

    def test_tags(self):
        self._test_on_files(self.big, 'out/next_and_done.todo', '@next and @done')
        self._test_on_files(self.big, 'out/due.todo', '@due < 2013-04-28')
        self._test_on_files(self.big, 'out/due-and-not-done.todo', '@due < 2013-04-28 and not @done')

    def test_parent(self):
        self._test_on_files(self.big, 'out/parentA.todo', 'parent contains A')

    def test_plus_d(self):
        self._test_on_files(self.big, 'out/task1+d.todo', 'task1 +d')

    def test_misc(self):
        self._test_on_files(self.big, 'out/misc1.todo', 'index = 1 and (@done or level = 1)')
        self._test_on_files(self.big, 'out/misc2.todo', '9 or (7 and not @done)')

    def test_add_remove(self):
        project_id = self.big.find_project_id_by_title('ProjectC')
        tp.add_new_subtask(project_id, 'abc')
        self._test_on_files(self.big, 'out/add_abc.todo')
        self.big.remove(project_id)
        self._test_on_files(self.big, 'out/removeC.todo')
        self.big = load_big()  # restart big
# run
unittest.main()
