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



class TodosAssTestCase(unittest.TestCase):
    def assertTodos(self, todos, text):
        self.assertEqual('\n'.join(t.get_text() for t in todos), text)

class TestGetOtherTodos(TodosAssTestCase):
    def test_parent(self):
        todos = Todos("""a
\tb
\t\tc
\t\t\td
""")
        self.assertTodos(todos.yield_parent(), '')
        self.assertTodos(todos.subitems[0].yield_parent(), '')
        self.assertTodos(todos.subitems[0].subitems[0].yield_parent(), 'a')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_parent(), '\tb')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].subitems[0].yield_parent(), '\t\tc')

    def test_ancestors(self):
        todos = Todos("""a
\tb
\t\tc
\t\t\td""")
        self.assertTodos(todos.yield_ancestors(), '')
        self.assertTodos(todos.subitems[0].yield_ancestors(), '')
        self.assertTodos(todos.subitems[0].subitems[0].yield_ancestors(), 'a\n')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_ancestors(), '\tb\na\n')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].subitems[0].yield_ancestors(), '\t\tc\n\tb\na\n')

    def test_yield_children(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\t\t\td""")
        self.assertTodos(todos.yield_children(), ('a'))
        self.assertTodos(todos.subitems[0].yield_children(), ('\tb'))
        self.assertTodos(todos.subitems[0].subitems[0].yield_children(), ('\t\tc\n\t\tc\n\t\tx'))

    def test_yield_descendants(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\t\t\td""")
        self.assertTodos(todos.yield_descendants(), str(todos))
        self.assertTodos(todos.subitems[0].yield_descendants(), """\tb
\t\tc
\t\tc
\t\tx
\t\t\td""")
        self.assertTodos(todos.subitems[0].subitems[0].yield_descendants(), """\t\tc
\t\tc
\t\tx
\t\t\td""")

    def test_yield_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.yield_siblings(), '')
        self.assertTodos(todos.subitems[0].yield_siblings(), 'a')
        self.assertTodos(todos.subitems[0].subitems[0].yield_siblings(), '\tb\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_siblings(), '\t\tc\n\t\tc\n\t\tx')

    def test_following_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.yield_following_siblings(), '')
        self.assertTodos(todos.subitems[0].yield_following_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].yield_following_siblings(), '\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_following_siblings(), '\t\tc\n\t\tx')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].yield_following_siblings(), '\t\tx')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].yield_following_siblings(), '')

    def test_preceding_siblings(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.yield_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].yield_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].yield_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_preceding_siblings(), '')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].yield_preceding_siblings(), '\t\tc')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].yield_preceding_siblings(), '\t\tc\n\t\tc')

    def test_following(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.yield_following(), 'a\n\tb\n\t\tc\n\t\tc\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].yield_following(), '\tb\n\t\tc\n\t\tc\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].yield_following(), '\t\tc\n\t\tc\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_following(), '\t\tc\n\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].yield_following(), '\t\tx\n\td')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].yield_following(), '\td')
        self.assertTodos(todos.subitems[0].subitems[1].yield_following(), '')

    def test_preceding(self):
        todos = Todos("""a
\tb
\t\tc
\t\tc
\t\tx
\td""")
        self.assertTodos(todos.yield_preceding(), '')
        self.assertTodos(todos.subitems[0].yield_preceding(), '')
        self.assertTodos(todos.subitems[0].subitems[0].yield_preceding(), '')
        self.assertTodos(todos.subitems[0].subitems[1].yield_preceding(), '\tb')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[0].yield_preceding(), '')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[1].yield_preceding(), '\t\tc')
        self.assertTodos(todos.subitems[0].subitems[0].subitems[2].yield_preceding(), '\t\tc\n\t\tc')
        self.assertTodos(todos.subitems[0].subitems[1].yield_preceding(), '\tb')


class TodosAsStringTestCase(unittest.TestCase):
    def assertTodos(self, todos, text):
        self.assertEqual(str(todos), text)


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
