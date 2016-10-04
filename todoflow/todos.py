# -*- coding: utf-8 -*-
from collections import deque

from .todoitem import Todoitem
from .query import Query
from .compatibility import unicode



class Todos(object):
    def __init__(self, todoitem=None, subitems=None, parent=None):
        """Representation of taskpaper todos."""
        self.todoitem = todoitem
        self.subitems = [Todos(c.todoitem, c.subitems, self) for c in subitems] if subitems else []
        self.parent = parent

    def __unicode__(self):
        strings = [unicode(i) for i in self.subitems]
        if self.todoitem:
            strings = [unicode(self.get_text())] + strings
        return '\n'.join(strings)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return 'Todos("{}")'.format(self.get_text())

    def __len__(self):
        return 1

    def __iter__(self):
        yield self
        for child in self.subitems:
            for descendant in child:
                yield descendant

    def __contains__(self, node_or_todoitem):
        pass  # TODO

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
        pass  # TODO

    def get_ancestors(self):
        pass  # TODO

    def get_children(self):
        pass  # TODO

    def get_descendants(self):
        pass  # TODO

    def get_siblings(self):
        pass  # TODO

    def get_following_siblings(self):
        pass  # TODO

    def get_following(self):
        pass  # TODO

    def get_preceding_siblings(self):
        pass  # TODO

    def get_preceding(self):
        pass  # TODO

    def append_child(self, child):
        if isinstance(child, Todoitem):
            node = Todos(todoitem, [], self)
        else:
            node = child
        self.subitems.append(node)

    def filter(self, query):
        pass

    def search(self, query):
        pass
