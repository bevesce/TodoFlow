from __future__ import unicode_literals

import unittest

import todoflow
from todoflow.compatibility import unicode


class TestTodoitem(unittest.TestCase):
    def test_task(self):
        task = todoflow.todoitem.Todoitem('- task')
        self.assertTrue(task.is_task)
        self.assertEqual('task', task.text)
        self.assertEqual('- task', unicode(task))

    def test_project(self):
        task = todoflow.todoitem.Todoitem('project:')
        self.assertTrue(task.is_project)
        self.assertEqual('project', task.text)
        self.assertEqual('project:', unicode(task))

    def test_note(self):
        task = todoflow.todoitem.Todoitem('note')
        self.assertTrue(task.is_note)
        self.assertEqual('note', task.text)
        self.assertEqual('note', unicode(task))


class TestTodosArthmetics(unittest.TestCase):
    def setUp(self):
        self.t1 = todoflow.Todos('- task 1')
        self.t2 = todoflow.Todos('- task 2')

    def test_add_headless(self):
        self.assertEqual(
            unicode(self.t1 + self.t2),
"""- task 1
- task 2"""
        )

    def test_head_to_headless(self):
        self.t1 = self.t1.as_subtodos_of('project 1:')
        self.assertEqual(
            unicode(self.t1 + self.t2),
"""project 1:
\t- task 1
- task 2"""
        )

    def test_headless_to_head(self):
        self.t1 = self.t1.as_subtodos_of('project 1:')
        self.assertEqual(
            unicode(self.t2 + self.t1),
"""- task 2
project 1:
\t- task 1"""
        )

    def test_head_to_head(self):
        self.t1 = self.t1.as_subtodos_of('project 1:')
        self.t2 = self.t2.as_subtodos_of('project 2:')
        self.assertEqual(
            unicode(self.t1 + self.t2),
"""project 1:
\t- task 1
project 2:
\t- task 2"""
        )


class TestTodosModification(unittest.TestCase):
    def todos(self, text):
        self._todos = todoflow.Todos(text)
        return self

    def with_text(self, text):
        self._text = text
        return self

    def appended_to_result_of_get(self, query):
        item = self._todos.get_item(query)
        self._todos = self._todos.by_appending(self._text, to_item=item)
        return self

    def prepend_to_result_of_get(self, query):
        item = self._todos.get_item(query)
        self._todos = self._todos.by_prepending(self._text, to_item=item)
        return self

    def are(self, text):
        self.assertEqual(unicode(self._todos), text)
        return self

    def test_append(self):
        self.todos(
"""- 0
p1:
\t- 1
- 2"""
        ).with_text('- 1.1').appended_to_result_of_get('p1').are(
"""- 0
p1:
\t- 1
\t- 1.1
- 2"""
        ).with_text('- 2.1').appended_to_result_of_get('2').are(
"""- 0
p1:
\t- 1
\t- 1.1
- 2
\t- 2.1"""
        )

    def test_prepend(self):
        self.todos(
"""- 0
p1:
\t- 1
- 2"""
        ).with_text('- 1.1').prepend_to_result_of_get('p1').are(
"""- 0
p1:
\t- 1.1
\t- 1
- 2"""
        ).with_text('- 2.1').prepend_to_result_of_get('2').are(
"""- 0
p1:
\t- 1.1
\t- 1
- 2
\t- 2.1"""
        )

if __name__ == '__main__':
    unittest.main()
