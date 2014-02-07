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

from lexer import Lexer
from todolist import TodoList
from item import NewLineItem, Task, Project, Note

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    @staticmethod
    def list_from_file(filepath):
        with open(filepath, 'r') as f:
            tlist = Parser(Lexer([l.decode('utf-8') for l in f.readlines()])).parse()
            tlist.source = filepath
            return tlist

    @staticmethod
    def list_from_text(text):
        tlist = Parser(Lexer([l.decode('utf-8') for l in text.split('\n')])).parse()
        return tlist

    def parse(self):
        def todolist(newlines_prefix = None):
            """parse list"""
            if not newlines_prefix:
                newlines_prefix = []
            type_on_top = self.lexer.top().type
            new_item = None

            type_to_constructor = {
                'task': Task,
                'project-title': Project,
                'note': Note,
            }

            # depending on type on top of input
            # construct appropriate object
            newlines = []
            while type_on_top == 'newline':
                self.lexer.pop()
                type_on_top = self.lexer.top().type
                newlines.append(NewLineItem())
            if type_on_top in type_to_constructor:
                new_item = parse_item(type_to_constructor[type_on_top])
            elif type_on_top == 'indent':  # begining of sublist
                self.lexer.pop()
                new_item = parse_sublist(newlines)
                newlines = []
            elif type_on_top in ('dedent', '$'):
                return TodoList(newlines_prefix + newlines)
            if isinstance(new_item, TodoList):
                return TodoList(newlines_prefix + newlines) + new_item  # + todolist() 
            return TodoList(newlines_prefix + newlines + [new_item]) + todolist()

        def parse_item(constructor):
            """parse Project, Task or Note with its subtasks"""
            lex = self.lexer.pop()
            sublist = None
            type_on_top = self.lexer.top().type

            newlines = []
            while type_on_top == 'newline':
                self.lexer.pop()
                type_on_top = self.lexer.top().type
                newlines.append(NewLineItem())
            sublist = TodoList(newlines)
            if type_on_top == 'indent':
                self.lexer.pop()
                sublist += parse_sublist()
            return constructor(
                text=lex.text,
                indent_level=lex.indent_level,
                sublist=sublist,
            )

        def parse_sublist(newlines_prefix=None):
            """parse part that begins with indent token"""
            sublist = todolist(newlines_prefix)
            type_on_top = self.lexer.top().type
            if type_on_top == 'dedent':  # don't eat $
                self.lexer.pop()
            return sublist

        return todolist()
