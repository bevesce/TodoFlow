from collections import deque

from .todoitem import Todoitem
from .querying.parser import parse as parse_query
from .printers import PlainPrinter


class Todos(object):
    def __init__(self, todos_tree):
        self.todos_tree = todos_tree

    def __iter__(self):
        return self.todos_tree.iter_values()

    def __unicode__(self):
        return PlainPrinter().unicode(self.todos_tree)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __len__(self):
        return len(self.todos_tree)

    def search(self, query):
        return self.todos_tree.search(
            parse_query(query)
        )

    def filter(self, query):
        filtered_tree = self.todos_tree.filter(
            parse_query(query)
        )
        return Todos(filtered_tree)

    def get_item(self, query):
        for i in self.search(query):
            return i


class TreeNode(object):
    def __init__(self, value=None, children=None, parent=None):
        self._value = value
        self._parent = parent
        self._children = None
        self.set_children(children)

    def __len__(self):
        return len(self.get_values())

    def __iter__(self):
        """deep first"""
        yield self
        for child in self._children:
            for grandchild in child:
                yield grandchild

    def iter_values(self):
        return (n.get_value() for n in self if n.get_value())

    def set_children(self, children):
        self._children = list(children) if children else []
        for c in self._children:
            c._parent = self

    def get_value(self):
        return self._value

    def get_values(self):
        return tuple(self.iter_values())

    def set_value(self, value):
        self._value = value

    def append(self, value):
        new_node = self._creat_new_node(value)
        self.append_child(new_node)

    def append_child(self, child):
        child._parent = self
        self._children.append(child)

    def prepend(self, value):
        new_node = self._creat_new_node(value)
        self.prepend_child(new_node)

    def prepend_child(self, child):
        child._parent = self
        self._children.insert(0, child)

    def _creat_new_node(self, value):
        return TreeNode(value=value, parent=self)

    def get_parent(self):
        return self._parent

    def get_children(self):
        return self._children

    def iter_parents(self):
        node = self
        while node._parent:
            yield node._parent
            node = node._parent

    def get_parents(self):
        return tuple(self.iter_parents())

    def get_level(self):
        return len(self.get_parents())

    def iter_parents_values(self):
        return (p.get_value() for p in self.iter_parents() if p.get_value())

    def get_parents_values(self):
        return tuple(self.iter_parents_values())

    def filter(self, text_or_query):
        return Todos(
            items=[i for i in [i.filter(text_or_query) for i in self.items] if i]
        )

    def filter(self, query):
        children_result = self._filter_children(query)
        if children_result:
            return TreeNode(value=self.get_value(), children=children_result)
        elif query(self):
            return TreeNode(value=self.get_value())
        return None

    def _filter_children(self, query):
        children_result_with_nones = [c.filter(query) for c in self.get_children()]
        return [c for c in children_result_with_nones if c]

    def search(self, query):
        return (n.get_value() for n in self if n.get_value() and query(n))

    def find(self, value):
        for node in self:
            if node.get_value() == value:
                return node
