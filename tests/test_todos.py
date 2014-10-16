from __future__ import unicode_literals

import unittest
from unittest_extensions import SeriesTestCase

import todoflow as tf
import resources.lists_to_test as lt


class TestTodosCreation(unittest.TestCase):
    def test_from_text(self):
        self.assertEqual(lt.t1, unicode(tf.from_text(lt.t1)))

    def test_remove(self):
        text = '- t\n- q'
        t = tf.from_text(text)
        q = t.get_item('q')
        t.remove(q)
        self.assertEqual('- t', unicode(t))
        text = '- t\n- q\n - w\n - v'
        t = tf.from_text(text)
        q = t.get_item('w')
        t.remove(q)
        self.assertEqual('- t\n- q\n - v', unicode(t))
        self.assertEqual(' - w', unicode(q))
        q.edit(' x:')
        self.assertEqual(' - x', unicode(q))

    def test_from_path(self):
        path = 'tests/resources/todos_test1.taskpaper'
        with open(path, 'r') as f:
            todos_text = f.read().decode('utf-8')
        todos = tf.from_path(path)
        self.assertEqual(todos_text, unicode(todos))
        self.assertEqual(path, todos.source)

    def test_from_paths(self):
        path = 'tests/resources/todos_test1.taskpaper'
        title = 'todos_test1:'
        with open(path, 'r') as f:
            todos_text = f.read().decode('utf-8')
        lines = ['    ' + s for s in todos_text.splitlines()]
        lines.append('')
        # lines2.append('')
        text = '\n'.join([title] + lines + [title] + lines)
        todos = tf.from_paths([path, path])
        self.assertEqual(text, str(todos))

        text = '\n'.join([title] + lines + [title] + lines + [title] + lines)
        todos = tf.from_paths([path, path, path])
        self.assertEqual(text, str(todos))

    def test_indend_dedent_todos(self):
        text = 't:\n    - t\n    - k'
        todos = tf.from_text(text)
        todos.indent()
        self.assertEqual('    t:\n        - t\n        - k', str(todos))
        todos.dedent()
        self.assertEqual(text, str(todos))
        todos.dedent()
        self.assertEqual('t:\n- t\n- k', str(todos))

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
        self.assertTrue(item.is_task())
        item.change_to_project()
        self.assertEqual('y:', str(item))
        self.assertTrue(item.is_project())
        item.change_to_note()
        self.assertEqual('y', str(item))
        self.assertTrue(item.is_note())

if __name__ == '__main__':
    unittest.main()
