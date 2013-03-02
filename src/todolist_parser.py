"""
# Parser of todo list.

Top-down parser of grammar that is almost LL(1).
Conflict is resolved by prefering production 7 over 5.

## Grammar:

    1. TodoList -> Item TodoList .
    2. Item     -> Task SubTasks
    3.           | Project SubTasks
    4.           | Note SubTasks
    5.           | indent TodoList dedent
    6.           | NewLineItem
    7. SubTasks -> indent TodoList dedent
    8.           | .

"""

from todolist_lexer import Lexer
from todolist import TodoList, NewLineItem, Task, Project, Note


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    @staticmethod
    def list_from_file(filepath):
        with open(filepath, 'r') as f:
            tlist = Parser(Lexer(f.readlines())).parse()
            tlist.source = filepath
            return tlist

    def parse(self):
        def todolist():
            """parse list"""
            type_on_top = self.lexer.top().type
            new_item = None

            type_to_constructor = {
                'task': Task,
                'project-title': Project,
                'note': Note,
            }

            # depending on type on top of input
            # construct appropriate object
            if type_on_top == 'newline':
                self.lexer.pop()
                new_item = NewLineItem()
            elif type_on_top in type_to_constructor:
                new_item = parse_item(type_to_constructor[type_on_top])
            elif type_on_top == 'indent':  # begining of sublist
                new_item = parse_sublist()
            elif type_on_top in ('dedent', '$'):
                return TodoList()

            return TodoList([new_item]) + todolist()

        def parse_item(constructor):
            """parse Project, Task or Note with its subtasks"""
            lex = self.lexer.pop()
            sub_tasks = None
            type_on_top = self.lexer.top().type
            if type_on_top == 'indent':
                sub_tasks = parse_sublist()
            return constructor(
                lex.text,
                lex.line_no,
                lex.indent_level,
                sub_tasks,
                )

        def parse_sublist():
            """parse part that begins with indent token"""
            self.lexer.pop()
            sublist = todolist()
            type_on_top = self.lexer.top().type
            if type_on_top == 'dedent':  # don't eat $
                self.lexer.pop()
            return sublist

        return todolist()
