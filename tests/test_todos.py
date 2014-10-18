from __future__ import unicode_literals

import unittest
from unittest_extensions import SeriesTestCase

import todoflow as tf
import resources.lists_to_test as lt


class TestTodosCreation(unittest.TestCase):
    def test_from_text(self):
        self.assertEqual(lt.t1, unicode(tf.from_text(lt.t1)))

    def test_from_path(self):
        path = 'tests/resources/todos_test1.taskpaper'
        with open(path, 'r') as f:
            todos_text = f.read().decode('utf-8')
        todos = tf.from_path(path)
        self.assertEqual(todos_text, unicode(todos))
        self.assertEqual(path, todos.source)

    def test_item(self):
        item = tf.todoitem.Todoitem.from_text('- y')
        item.tag('d', 1)
        self.assertTrue(item.has_tag('d'))
        self.assertEqual('1', item.get_tag_param('d'))
        item.remove_tag('d')
        self.assertFalse(item.has_tag('d'))
        item.indent()
        self.assertEqual('    - y', str(item))
        item.dedent()
        self.assertEqual('- y', str(item))
        item.dedent()
        self.assertEqual('- y', str(item))
        self.assertTrue(item.is_task)
        item.change_to_project()
        self.assertEqual('y:', str(item))
        self.assertTrue(item.is_project)
        item.change_to_note()
        self.assertEqual('y', str(item))
        self.assertTrue(item.is_note)

if __name__ == '__main__':
    unittest.main()
