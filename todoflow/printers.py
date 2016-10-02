"""Printers that can be used to output `Todos` in several formats."""

from __future__ import unicode_literals
import datetime as dt
import bisect

from . import textutils as tu
from . import config


class AbstractPrinter(object):
    """Implements basic structure of Printer,
    so other printers that inherit from it can only implement:

    - `format_task_text`
    - `format_project_text`
    - `format_note_text`
    - `format_empty_line_text`

    or

    - `convert_task`
    - `convert_project`
    - `convert_note`
    - `convert_empty_line`

    `format_..._text` methods receive only text of item
    `convert_...` methods receive item and the node that contains it

    """
    indention = config.indention

    def __call__(self, todos_tree):
        self.pprint(todos_tree)

    def pprint(self, todos_tree):
        print(self.pformat(todos_tree))

    def pformat(self, todos_tree):
        todos_tree = self._eject_tree(todos_tree)
        return '\n'.join(self.convert_to_list(todos_tree))

    def _eject_tree(self, todos_tree):
        try:
            return todos_tree._todos_tree
        except AttributeError:
            return todos_tree

    def convert_to_list(self, todos_tree):
        converted_nodes = [self.convert_node(n) for n in todos_tree]
        return [n for n in converted_nodes if n is not None]

    def convert_node(self, node):
        item = node.get_value()
        if item:
            return self.convert_item(item, node)

    def convert_item(self, item, node=None):
        if item.is_task:
            converted = self.convert_task(item, node)
        elif item.is_project:
            converted = self.convert_project(item, node)
        elif item.is_note:
            converted = self.convert_note(item, node)
        elif item.is_empty_line:
            converted = self.convert_empty_line(item, node)
        else:
            return None
        if converted is not None:
            return self.make_indent(item, node) + converted

    def convert_task(self, item, node=None):
        return self.format_task_text(item.text)

    def convert_project(self, item, node=None):
        return self.format_project_text(item.text)

    def convert_note(self, item, node=None):
        return self.format_note_text(item.text)

    def make_indent(self, item, node):
        if item.is_empty_line:
            return ''
        indent_level = (len(node.get_parents_values())) if node else 0
        return self.indention * indent_level

    def convert_empty_line(self, item, node=None):
        return self.format_empty_line_text(item.text)

    def format_task_text(self, text):
        raise NotImplemented()

    def format_project_text(self, text):
        raise NotImplemented()

    def format_empty_line_text(self, text):
        raise NotImplemented()

    def format_note_text(self, text):
        raise NotImplemented()


class PlainPrinter(AbstractPrinter):
    """Basic printer that converts todos to plain text in .taskpaper format."""
    def format_task_text(self, text):
        return config.task_indicator + text

    def format_project_text(self, text):
        return text + config.project_indicator

    def format_empty_line_text(self, text):
        return ''

    def format_note_text(self, text):
        return text


pprint = PlainPrinter().pprint
