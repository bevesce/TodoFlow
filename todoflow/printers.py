from __future__ import unicode_literals


class PlainPrinter(object):
    def unicode(self, todos_tree):
        return '\n'.join([
            self.handle_item(n.get_value(), len(n.get_parents_values()))
            for n in todos_tree if n.get_value()
        ])

    def str(self, todos_tree):
        return self.unicode(todos_tree).encode('utf-8')

    def handle_item(self, todoitem, level):
        handler_type_map = {
            'is_task': self.handle_task,
            'is_project': self.handle_project,
            'is_note': self.handle_note,
            'is_empty_line': self.handle_empty_line,
        }
        for item_type, handler in handler_type_map.iteritems():
            if getattr(todoitem, item_type):
                return self.make_indent(todoitem, level) + handler(todoitem, level)

    def handle_task(self, todoitem, level):
        return '- ' + todoitem.text

    def handle_project(self, todoitem, level):
        return todoitem.text + ':'

    def handle_note(self, todoitem, level):
        return todoitem.text

    def handle_empty_line(self, todoitem, level):
        return ''

    def make_indent(self, todoitem, level):
        return ' ' * todoitem.indent_level
