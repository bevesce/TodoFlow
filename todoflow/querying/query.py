from __future__ import absolute_import

import todoflow.textutils as tu


class AbstractQuery(object):
    def matches(self, todonode):
        raise NotImplementedError


# Basic
class TextQuery(AbstractQuery):
    def matches(self, todonode):
        return self.matches_text(todonode.item.text)


class SubstringQuery(TextQuery):
    def __init__(self, text):
        self.text = text.lower()

    def matches_text(self, text):
        return self.text in text.lower()


class TagQuery(TextQuery):
    def __init__(self, tag):
        self.tag = tag

    def matches_text(self, text):
        return tu.has_tag(text, self.tag)


# Logical operators
class NotQuery(AbstractQuery):
    def __init__(self, query):
        self.query = query

    def matches(self, todonode):
        return not self.query.matches(todonode)

    def matches_text(self, text):
        return not self.query.matches_text(text)


class AbstractBinaryQuery(AbstractQuery):
    def __init__(self, query1, query2):
        self.query1 = query1
        self.query2 = query2

    def matches(self, todonode):
        return self.operation(self.query1.matches(todonode), self.query2.matches(todonode))

    def matches_text(self, text):
        return self.operation(self.query1.matches_text(text), self.query2.matches_text(text))


class AndQuery(AbstractBinaryQuery):
    operation = lambda _, a, b: a and b  # self is on first place


class OrQuery(AbstractBinaryQuery):
    operation = lambda _, a, b: a or b  # self is on first place


# ops
class TagOpQuery(TextQuery):
    def __init__(self, tag, operation=None, right_side=None):
        self.tag = tag
        self.operation = operation
        self.right_side = right_side.strip() if right_side else ''

    def matches_text(self, text):
        param = tu.get_tag_param(text, self.tag)
        if param is None:
            return False
        return self.operation(param, self.right_side)


class UpstreamNodeQuery(AbstractQuery):
    def matches(self, todonode):
        node = todonode
        while node:
            if self.node_matches(node):
                return True
            node = node.get_parent_node()


class ProjectOpQuery(UpstreamNodeQuery):
    def __init__(self, operation=None, right_side=None):
        self.operation = operation
        self.right_side = right_side.strip() if right_side else ''

    def node_matches(self, todonode):
        return (
            todonode.item.is_project() and
            self.operation(todonode.item.text, self.right_side)
        )


# whole list
class PlusDescendants(UpstreamNodeQuery):
    def __init__(self, query):
        self.query = query

    def node_matches(self, node):
        return self.query.matches(node)


class OnlyFirst(AbstractQuery):
    def __init__(self, query):
        self.query = query

    def matches(self, todonode):
        if not todonode.containing_todos:
            return True
        todos = todonode.containing_todos
        if not todos.items:
            return True
        return self._is_node_first_that_matches(todos.items, todonode)

    def _is_node_first_that_matches(self, items, todonode):
        matching_items = [n for n in items if self.query.matches(n)]
        return matching_items[0] == todonode if matching_items else False


class TypeOpQuery(AbstractQuery):
    def __init__(self, operation=None, right_side=None):
        self.operation = operation
        self.right_side = right_side

    def matches(self, todonode):
        return {
            'task': todonode.item.is_task(),
            'note': todonode.item.is_note(),
            'project': todonode.item.is_project(),
        }.get(self.right_side, False)


class UniqueidOpQuery(AbstractQuery):
    def __init__(self, operation=None, right_side=None):
        self.operation = operation
        self.right_side = right_side

    def matches(self, todonode):
        return self.operation(todonode.item.uniqueid, self.right_side)
