# -*- coding: utf-8 -*-
from collections import deque

from .todoitem import Todoitem
from .query import Query
from .printers import PlainPrinter
from .compatibility import unicode


class Todos(object):
    """Representation of taskpaper todos."""
    def __init__(self, todoitems):
        if isinstance(todoitems, unicode):
            from .parser import parse
            self.node = parse(todoitems)
        else:
            self.node = todoitems

    def __iter__(self):
        for node in self.node:
            yield node.todoitem

    def __unicode__(self):
        return str(self.node)

    def __str__(self):
        return self.__unicode__()

    def __len__(self):
        return sum(len(n) for n in self.node)

    def __add__(self, other):
        return Todos(self.node + other.node)

    def __div__(self, query):
        """Filter todos by query"""
        return self.filter(query)

    def iter_nodes(self):
        for node in self.node:
            yield node

    def filter(self, query):
        if isinstance(query, unicode):
            from .query_parser import parse as parse_query
            q = parse_query(query)
            return q.filter(self)
        filtered_nodes = self.nodes.filter(query)
        return Todos(filtered_nodes)

    def search(self, query):
        pass


class Node(object):
    def __init__(self, todoitem=None, children=None, parent=None):
        """
        Args:
            todoitem ()
            children (iterable of `Node`)
            parent (`Node`)
            source (text)
        """
        self.todoitem = todoitem
        self.children = [Node(c.todoitem, c.children, self) for c in children] if children else []
        self.parent = parent

    def __unicode__(self):
        rest = ''
        self_string = self.get_text()
        children_string = '\n'.join(c.get_text() for c in self.children)
        if not self.todoitem:
            return children_string
        if self.children:
            return self_string + '\n' + children_string
        return self_string

    def __str__(self):
        return self.__unicode__()

    def __len__(self):
        return 1 + len(list(self.get_descendants()))

    def __iter__(self):
        yield self
        for child in self.children:
            for descendant in child:
                yield descendant

    def __add__(self, other):
        self_value, other_value = self.todoitem, other.todoitem
        if self_value and other_value:
            return Node(children=[self, other])
        elif self_value:
            return Node(children=[self] + other.children)
        elif other_value:
            return Node(children=self.children + [other])
        else:
            return Node(children=self.children + other.children)

    def get_text(self):
        if not self.todoitem:
            return ''
        return '\t' * self.get_level() + self.todoitem.get_text()

    def get_level(self):
        return len(list(self.get_ancestors())) - 1

    def get_id(self):
        return self.todoitem.id

    def get_line_number(self):
        return self.todoitem.line_number

    def get_tag_param(self, tag):
        return self.todoitem.get_tag_param(tag)

    def get_type(self):
        return self.todoitem.type

    def get_parent(self):
        return self.parent

    def get_ancestors(self):
        node = self
        while node.parent:
            yield node.parent
            node = node.parent

    def get_children(self):
        for child in self.children:
            yield child

    def get_descendants(self):
        for child in self.children:
            yield child
            for descendant in child.get_descendants():
                yield descendant

    def get_siblings(self):
        if not self.parent:
            return []
        return self.parent.children

    def get_following_siblings(self):
        siblings = self.get_siblings()
        index = siblings.index(self)
        for node in siblings[index + 1:]:
            yield node

    def get_preceding_siblings(self):
        siblings = self.get_siblings()
        index = siblings.index(self)
        for node in siblings[:index]:
            yield node

    def append_child(self, node):
        child = Node(node.todoitem, node.children, self)
        self.children.append(child)

    def filter(self, query):
        """
        Args:
            query (`Query`)

        Returns:
            New `Node` with only this subnodes that match query.
        """
        children_result = self._filter_children(query)
        new_node = None
        if children_result:
            new_node = Node(
                todoitem=self.get_value(), children=children_result, source=self.source
            )
        elif query(self):
            new_node = Node(todoitem=self.get_value(), source=self.source)
        return new_node

    def _filter_children(self, query):
        children_result_with_nones = [c.filter(query) for c in self.get_children()]
        return [c for c in children_result_with_nones if c]

    def search(self, query):
        """
        Args:
            query (`Query`)

        Returns:
            Iterator of `Todoitem`s in this `Node` that match query.
        """
        return (n.get_value() for n in self if n.get_value() and query(n))
