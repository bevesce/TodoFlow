# -*- coding: utf-8 -*-
from collections import deque

from .todoitem import Todoitem
from .query import Query
from .compatibility import unicode, is_string



class Todos(object):
    def __init__(self, todoitem=None, subitems=None, parent=None):
        """Representation of taskpaper todos."""
        if is_string(todoitem):
            from .parser import parse
            todos = parse(todoitem)
            self.todoitem = None
            self.subitems = todos.subitems
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

    def __contains__(self, todos_or_todoitem):
        for subitem in self:
            if subitem is todos_or_todoitem:
                return True
            if subitem.todoitem and subitem.todoitem is todos_or_todoitem:
                return True
        return False

    def __iter__(self):
        if self.todoitem:
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

    def __div__(self, query):
        return self.filter(query)

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

    def get_with_todoitem(self, todoitem):
        for subitem in self:
            if subitem.todoitem == todoitem:
                return subitem
        raise KeyError('{} not found in {}'.format(todoitem, self))

    def get_level(self):
        level = 0
        todos = self
        while todos.parent:
            if todos.parent.todoitem:
                level += 1
            todos = todos.parent
        return level

    def get_id(self):
        if not self.todoitem:
            return None
        return self.todoitem.get_id()

    def get_line_number(self):
        if not self.todoitem:
            return None
        return self.todoitem.get_line_number()

    def get_type(self):
        if not self.todoitem:
            return None
        return self.todoitem.get_type()

    def get_tag_param(self, tag):
        if not self.todoitem:
            return None
        return self.todoitem.get_tag_param(tag)

    def has_tag(self, tag):
        if not self.todoitem:
            return False
        return self.todoitem.has_tag(tag)

    def yield_parent(self):
        if self.parent:
            yield self.parent

    def yield_ancestors(self):
        for parent in self.yield_parent():
            for ancestor in parent.yield_ancestors_and_self():
                yield ancestor

    def yield_ancestors_and_self(self):
        ancestor_or_self = self
        while ancestor_or_self:
            yield ancestor_or_self
            ancestor_or_self = ancestor_or_self.parent

    def yield_children(self):
        for child in self.subitems:
            yield child

    def yield_descendants(self):
        for child in self.subitems:
            for descendant in child:
                yield descendant

    def yield_descendants_and_self(self):
        for descendant_or_self in self:
            yield descendant_or_self

    def yield_siblings(self):
        for parent in self.yield_parent():
            for sibling in parent.yield_children():
                yield sibling

    def yield_following_siblings(self):
        started = False
        for sibling in self.yield_siblings():
            if started:
                yield sibling
            elif sibling is self:
                started = True

    def yield_preceding_siblings(self):
        finished = False
        for sibling in self.yield_siblings():
            if sibling is self:
                finished = True
            if not finished:
                yield sibling

    def yield_following(self):
        for child in self.yield_descendants():
            yield child
        for ancestor in self.yield_ancestors_and_self():
            for sibling in ancestor.yield_following_siblings():
                yield sibling

    def yield_preceding(self):
        for ancestor in self.yield_ancestors_and_self():
            for sibling in ancestor.yield_preceding_siblings():
                yield sibling

    def append(self, subitem):
        self.subitems.append(self.maybe_make_todos(subitem))

    def insert(self, index, subitem):
        self.subitems.insert(index, self.maybe_make_todos(subitem))

    def maybe_make_todos(self, child):
        if isinstance(child, Todoitem):
            return Todos(todoitem, [], self)
        return child

    def filter(self, query):
        if is_string(query):
            from .query_parser import parse
            query = parse(query)
        if isinstance(query, Query):
            matching = list(query.search(self))
            query = lambda i: i in matching
        subitems = [i for i in [i.filter(query) for i in self.subitems] if i]
        if subitems or query(self):
            return Todos(self.todoitem, subitems=subitems)
        return Todos()

    def search(self, query):
        if is_string(query):
            from .query_parser import parse
            query = parse(query)
        if isinstance(query, Query):
            for item in query.search(self):
                yield item
            return
        for item in self:
            if query(item):
                yield item
