from collections import deque

from .todoitem import Todoitem
from .querying.parser import parse as parse_query
from .printers import PlainPrinter
from .compatibility import _str_


class Todos(object):
    def __init__(self, todos_tree=None, source=None):
        self.todos_tree = todos_tree or TreeNode()
        self._source = source
        self.todos_tree.source = source

    def __iter__(self):
        return self.todos_tree.iter_values()

    def __unicode__(self):
        return PlainPrinter().unicode(self.todos_tree) if self.todos_tree else u''

    def __str__(self):
        return _str_(self)

    def __len__(self):
        return len(self.todos_tree)

    def __add__(self, other):
        return Todos(self.todos_tree + other.todos_tree)

    def __div__(self, query):
        # I know it's inresponsible but is't so cool
        return self.filter(query)

    def set_source(self, path):
        self._source = path
        self.todos_tree.source = path

    def get_source(self):
        if self._source:
            return self._source
        else:
            return self.todos_tree.source

    def search(self, query):
        return self.todos_tree.search(parse_query(query))

    def filter(self, query):
        filtered_tree = self.todos_tree.filter(
            parse_query(query)
        )
        return Todos(filtered_tree, source=self._source)

    def get_item(self, query):
        for i in self.search(query):
            return i

    def set_master_item(self, text):
        self.todos_tree.set_value(Todoitem(text))

    def iter_sourced(self):
        for node in self.todos_tree:
            if node.source:
                yield Todos(
                    TreeNode(children=node.get_children()),
                    source=node.source
                )


class TreeNode(object):
    def __init__(self, value=None, children=None, parent=None, source=None):
        self._value = value
        self._parent = parent
        self._children = None
        self.set_children(children)
        self.source = source

    def __len__(self):
        return len(self.get_values())

    def __iter__(self):
        yield self
        for child in self._children:
            for grandchild in child:
                yield grandchild

    def __add__(self, other):
        self_value, other_value = self.get_value(), other.get_value()
        if self_value and other_value:
            return TreeNode(children=[self, other])
        elif self_value:
            return TreeNode(children=[self] + other._children)
        elif other_value:
            return TreeNode(children=self._children + [other])
        else:
            return TreeNode(children=self._children + other._children)

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
        new_node = None
        if children_result:
            new_node = TreeNode(
                value=self.get_value(), children=children_result, source=self.source
            )
        elif query(self):
            new_node = TreeNode(value=self.get_value(), source=self.source)
        return new_node

    def _filter_children(self, query):
        children_result_with_nones = [c.filter(query) for c in self.get_children()]
        return [c for c in children_result_with_nones if c]

    def search(self, query):
        return (n.get_value() for n in self if n.get_value() and query(n))

    def find(self, value):
        for node in self:
            if node.get_value() == value:
                return node
