# -*- coding: utf-8 -*-
from collections import deque

from .todoitem import Todoitem
from .query import Query
from .compatibility import unicode



class Todos(object):
    def __init__(self, todoitem=None, subitems=None, parent=None):
        """Representation of taskpaper todos."""
        if isinstance(todoitem, unicode):
            from .parser import parse
            node = parse(todoitem)
            self.todoitem = None
            self.subitems = node.subitems
            self.parent = None
        else:
            self.todoitem = todoitem
            self.subitems = [Todos(c.todoitem, c.subitems, self) for c in subitems] if subitems else []
            self.parent = parent

    def __add__(self, other):
        self_value, other_value = self.todoitem, other.todoitem
        if self_value and other_value:
            return Todos(subitems=[self, other])
        elif self_value:
            return Todos(subitems=[self] + other.subitems)
        elif other_value:
            return Todos(subitems=self.subitems + [other])
        else:
            return Todos(subitems=self.subitems + other.subitems)

    def __bool__(self):
        return bool(self.todoitem or self.subitems)

    def __contains__(self, node_or_todoitem):
        for subitem in self:
            if subitem is node_or_todoitem:
                return True
            if subitem.todoitem and subitem.todoitem is node_or_todoitem:
                return True
        return False

    def __getitem__(self, todoitem):
        for subitem in self:
            if subitem.todoitem == todoitem:
                return subitem
        raise KeyError('{} not found in {}'.format(todoitem, self))

    def __iter__(self):
        yield self
        for child in self.subitems:
            for descendant in child:
                yield descendant

    def __len__(self):
        return sum(len(i) for i in self.subitems) + (1 if self.todoitem else 0)

    def __repr__(self):
        return 'Todos("{}")'.format(self.get_text())

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        strings = [unicode(i) for i in self.subitems]
        if self.todoitem:
            strings = [unicode(self.get_text())] + strings
        return '\n'.join(strings)

    def get_text(self):
        if not self.todoitem:
            return ''
        if self.todoitem.get_type() == 'newline':
            return ''
        return '\t' * self.get_level() + self.todoitem.get_text()

    def get_level(self):
        level = 0
        node = self
        while node.parent:
            if node.parent.todoitem:
                level += 1
            node = node.parent
        return level

    def get_id(self):
        return self.todoitem.get_id()

    def get_line_number(self):
        return self.todoitem.get_line_number()

    def get_tag_param(self, tag):
        return self.todoitem.get_tag_param(tag)

    def get_type(self):
        return self.todoitem.get_type()

    def get_parent(self):
        if self.parent:
            return Todos(self.parent.todoitem)
        return Todos()

    def get_ancestors(self):
        if not self.parent:
            return Todos()
        node = self.parent
        ancestors = []
        while node.parent:
            ancestors = [Todos(node.todoitem, subitems=ancestors)]
            node = node.parent
        if not ancestors:
            return Todos()
        return ancestors[0]

    def get_children(self):
        return Todos(subitems=[Todos(c.todoitem) for c in self.subitems])

    def get_descendants(self):
        return Todos(subitems=self.subitems)

    def get_siblings(self):
        if not self.parent:
            return Todos()
        return self.parent.get_children()

    def get_following_siblings(self):
        siblings = self.get_siblings()
        if not siblings.subitems:
            return Todos()
        return Todos(
            subitems=siblings.subitems[siblings.index(self.todoitem) + 1:]
        )

    def get_preceding_siblings(self):
        siblings = self.get_siblings()
        if not siblings.subitems:
            return Todos()
        return Todos(
            subitems=siblings.subitems[:siblings.index(self.todoitem)]
        )

    def get_following(self):
        if not self.parent:
            return Todos()
        node = self
        following = []
        while node.parent:
            index = node.parent.subitems.index(node)
            following = [Todos(node.parent.todoitem, subitems=following + node.parent.subitems[index + 1:])]
            node = node.parent
        if not following:
            return Todos()
        return following[0]

    def get_preceding(self):
        if not self.parent:
            return Todos()
        node = self
        preceding = []
        while node.parent:
            index = node.parent.subitems.index(node)
            preceding = [Todos(node.parent.todoitem, subitems=preceding + node.parent.subitems[:index])]
            node = node.parent
        if not preceding:
            return Todos()
        return preceding[0]

    def index(self, todoitem):
        for index, todos in enumerate(self.subitems):
            if todos.todoitem == todoitem:
                return index
        raise ValueError('{} not found in {}'.format(todoitem, self))

    def append_child(self, child):
        if isinstance(child, Todoitem):
            node = Todos(todoitem, [], self)
        else:
            node = child
        self.subitems.append(node)

    def filter(self, query):
        if isinstance(query, unicode):
            from .query_parser import parse
            return parse(query).filter(self)
        if isinstance(query, Query):
            return query.filter(self)
        subitems = [i for i in [i.filter(query) for i in self.subitems] if i]
        if subitems or query(self.todoitem):
            return Todos(self.todoitem, subitems=subitems)
        return Todos()

    def search(self, query):
        if isinstance(query, unicode):
            from .query_parser import parse
            return parse(query).search(self)
        if isinstance(query, Query):
            return query.search(self)
        for subitem in self:
            if query(subitem.todoitem):
                yield subitem.todoitem
