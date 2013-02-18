from todolist_lexer import *
from todolist import *


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    @staticmethod
    def from_file(filepath):
        with open(filepath, 'r') as f:
            tlist = Parser(Lexer(f.readlines())).parse()
            tlist.source = filepath
            return tlist

    def parse(self):
        self.ii = 0

        def todolist():
            self.ii += 1
            # if self.ii > 100:
            #     return TodoList()
            top_type = self.lexer.top().type
            if top_type == '$':
                return TodoList()

            p = None
            if top_type == 'newline':
                self.lexer.pop()
                p = NewLineItem()
            elif top_type == 'task':
                p = parse_item(constructor=Task)
            elif top_type == 'project-title':
                p = parse_item(constructor=Project)
            elif top_type == 'note':
                p = parse_item(constructor=Note)
            elif top_type == 'indent':
                self.lexer.pop()
                p = todolist()
                top_type = self.lexer.top().type
                if top_type == 'dedent':
                    self.lexer.pop()
            elif top_type in ('dedent', '$'):
                return TodoList()
            return TodoList([p]) + todolist()

        def parse_item(constructor):
            lex = self.lexer.pop()
            top_type = self.lexer.top().type
            sub_tasks = None
            if top_type == 'indent':
                self.lexer.pop()
                sub_tasks = todolist()
                top_type = self.lexer.top().type
                if top_type == 'dedent':
                    self.lexer.pop()
            return constructor(lex.text[0:-1], lex.line_no, lex.indent_level, sub_tasks)

        return todolist()
