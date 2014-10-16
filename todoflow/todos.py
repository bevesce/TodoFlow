from collections import deque

from .todoitem import Todoitem
from .querying.parser import parse as parse_query


class Todos(object):
    def __init__(self, items=None, source=None):
        self.parent_node = None
        self.source = source
        self.set_items(items)

    def __len__(self):
        return len(self.items)

    def __unicode__(self):
        return u'\n'.join([unicode(i) for i in self.items])

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __iter__(self):
        raise NotImplemented

    @property
    def items(self):
        return tuple(self.__items)

    def filter(self, text_or_query):
        text_or_query = self._convert_test_to_query(text_or_query)
        return Todos(
            items=[i for i in [i.filter(text_or_query) for i in self.items] if i]
        )

    def search(self, text_or_query):
        text_or_query = self._convert_test_to_query(text_or_query)
        result = []
        for item in self.__items:
            result += item.search(text_or_query)
        return result

    def _convert_test_to_query(self, text_or_query):
        return parse_query(text_or_query)

    def get_item(self, text_or_query):
        return self.search(text_or_query)[0]

    def set_items(self, items):
        self.__items = deque(items) if items else deque()
        for item in self.__items:
            self._add_parent(item)

    def _add_parent(self, item):
        item.containing_todos = self

    def append(self, item):
        self.__items.append(item)
        self._add_parent(item)

    def prepend(self, item1, *args):
        self.__items.appendleft(item)
        self._add_parent(item)

    def remove(self, item):
        found_node = self._find_node_with_item(item)
        if found_node:
            self._remove_node(found_node)
        else:
            self._propagate_remove_to_nodes(item)

    def _find_node_with_item(self, item):
        found_node = None
        for node in self.items:
            if node.item == item:
                found_node = node
        return found_node

    def _remove_node(self, node):
        self.__items.remove(node)
        node.containing_todos = None

    def _propagate_remove_to_nodes(self, item):
        for node in self.items:
            node.remove(item)

    def indent(self):
        for item in self.__items:
            item.indent()

    def dedent(self):
        for item in self.__items:
            item.dedent()

    def _class_repr(self):
        return '\n'.join(
            item._class_repr() for item in self.items
        )


class Todonode(object):
    def __init__(self, text=None, subtodos=None, item=None):
        self.containing_todos = None
        self.item = item or Todoitem.from_text(text)
        self.subtodos = subtodos or Todos()

    def __unicode__(self):
        if self.subtodos:
            return unicode(self.item) + u'\n' + unicode(self.subtodos)
        else:
            return unicode(self.item)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def subtodos(self):
        return self._subtodos

    @subtodos.setter
    def subtodos(self, value):
        self._subtodos = value
        value.parent_node = self

    def get_parent_node(self):
        if self.containing_todos:
            return self.containing_todos.parent_node
        else:
            return None

    def search(self, query):
        subtodos_result = self.subtodos.search(query)
        if query.matches(self):
            return [self.item] + subtodos_result
        else:
            return subtodos_result

    def filter(self, query):
        subtodos_result = self.subtodos.filter(query)
        if subtodos_result:
            return Todonode(item=self.item, subtodos=subtodos_result)
        elif query.matches(self):
            return Todonode(item=self.item)
        else:
            return None

    def remove(self, item):
        self.subtodos.remove(item)

    def indent(self):
        self.item.indent()
        self.subtodos.indent()

    def dedent(self):
        self.item.dedent()
        self.subtodos.dedent()

    def _class_repr(self, indent_level=0):
        me = ' ' * indent_level + self.item._text_formatter.__class__.__name__[0].lower()
        subs = [i._class_repr(indent_level=indent_level + 1) for i in self.subtodos.items]
        return '\n'.join([me] + subs)
