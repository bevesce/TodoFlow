from __future__ import unicode_literals

import unittest

import todoflow
from todoflow import Todos, Todoitem
from todoflow.compatibility import unicode


class TestTodoitem(unittest.TestCase):
    def test_task(self):
        task = todoflow.todoitem.Todoitem('- task')
        self.assertTrue(task.type == 'task')
        self.assertEqual('task', task.text)
        self.assertEqual('- task', unicode(task))

    def test_project(self):
        task = todoflow.todoitem.Todoitem('project:')
        self.assertTrue(task.type == 'project')
        self.assertEqual('project', task.text)
        self.assertEqual('project:', unicode(task))

    def test_note(self):
        task = todoflow.todoitem.Todoitem('note')
        self.assertTrue(task.type == 'note')
        self.assertEqual('note', task.text)
        self.assertEqual('note', unicode(task))


class TodosAsStringTestCase(unittest.TestCase):
    def assertTodos(self, todos, text):
        self.assertEqual(str(todos), text)


class TestGetOtherTodos(TodosAsStringTestCase):
    def test_get_parent(self):
        todos = Todos("""a
\tb
\t\tc
\t\t\td
""")
        self.assertTodos(todos.get_parent(), '')
        self.assertTodos(todos.subitems[0].get_parent(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_parent(), 'a')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_parent(), 'b')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].subitems[0].get_parent(), 'c')

    def test_get_ancestors(self):
        todos = Todos("""a
\tb
\t\tc
\t\t\td""")
        self.assertTodos(todos.get_ancestors(), '')
        self.assertTodos(todos.subitems[0].get_ancestors(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_ancestors(), 'a')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_ancestors(), 'a\n\tb')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].subitems[0].get_ancestors(), 'a\n\tb\n\t\tc')

    def test_get_children(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\t\t\td""")
        self.assertTodos(todos.get_children(), ('a'))
        self.assertTodos(todos.subitems[0].get_children(), ('b'))
        self.assertTodos(todos.subitems[0].subitems[0].get_children(), ('c\nc\nx'))

    def test_get_descendants(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\t\t\td""")
        self.assertTodos(todos.get_descendants(), str(todos))
        self.assertTodos(todos.subitems[0].get_descendants(), """b
\tc
\tc
\tx
\t\td""")
        self.assertTodos(todos.subitems[0].subitems[0].get_descendants(), """c
c
x
\td""")

    def test_get_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.get_siblings(), '')
        self.assertTodos(todos.subitems[0].get_siblings(), 'a')
        self.assertTodos(todos.subitems[0].subitems[0].get_siblings(), 'b\nd')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_siblings(), 'c\nc\nx')

    def test_following_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.get_following_siblings(), '')
        self.assertTodos(todos.subitems[0].get_following_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_following_siblings(), 'd')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_following_siblings(), 'c\nx')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].get_following_siblings(), 'x')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].get_following_siblings(), '')

    def test_preceding_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.get_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].get_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].get_preceding_siblings(), 'c')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].get_preceding_siblings(), 'c\nc')

    def test_following(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.get_following(), '')
        self.assertTodos(todos.subitems[0].get_following(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_following(), 'a\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_following(), 'a\n\tb\n\t\tc\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].get_following(), 'a\n\tb\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].get_following(), 'a\n\tb\n\td')
        self.assertTodos(todos.subitems[0].subitems[1].get_following(), 'a')

    def test_preceding(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.get_preceding(), '')
        self.assertTodos(todos.subitems[0].get_preceding(), '')
        self.assertTodos(todos.subitems[0].subitems[0].get_preceding(), 'a')
        self.assertTodos(todos.subitems[0].subitems[1].get_preceding(), 'a\n\tb\n\t\tc\n\t\tc\n\t\tx')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].get_preceding(), 'a\n\tb')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].get_preceding(), 'a\n\tb\n\t\tc')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].get_preceding(), 'a\n\tb\n\t\tc\n\t\tc')
        self.assertTodos(todos.subitems[0].subitems[1].get_preceding(), 'a\n\tb\n\t\tc\n\t\tc\n\t\tx')


class TestTodos(TodosAsStringTestCase):
    def test_add_todos(self):
        self.assertTodos(Todos('- t1') + Todos('- t2'), '- t1\n- t2')

    def test_add_todos_1(self):
        self.assertTodos(Todos('i:\n\t-q').subitems[0] + Todos('- t2'), 'i:\n\t-q\n- t2')

    def test_add_todos_1(self):
        self.assertTodos(Todos('- t2') + Todos('i:\n\t-q').subitems[0], '- t2\ni:\n\t-q')

    def test_get(self):
        todos = Todos('a\n\tb')
        subtodos = todos.subitems[0].subitems[0]
        self.assertEqual(todos.get_with_todoitem(subtodos.todoitem), subtodos)

    def test_filter(self):
        todos = Todos("""a
\tr
\t\tq
\tw
\t\tr
\te
\t\te
""").filter(lambda i: 'r' in i.get_text())
        self.assertTodos(todos, 'a\n\tr\n\tw\n\t\tr')


class TestContains(unittest.TestCase):
    def test_1(self):
        todos = Todos("""a:
\tb
\t\tc""")
        self.assertFalse(Todoitem('b') in todos)
        self.assertTrue(todos.subitems[0] in todos)
        self.assertTrue(todos.subitems[0].todoitem in todos)
        self.assertTrue(todos.subitems[0].subitems[0] in todos)
        self.assertTrue(todos.subitems[0].subitems[0].todoitem in todos)
        self.assertTrue(todos.subitems[0].subitems[0].subitems[0] in todos)
        self.assertTrue(todos.subitems[0].subitems[0].subitems[0].todoitem in todos)


if __name__ == '__main__':
    unittest.main()
