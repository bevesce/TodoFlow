from __future__ import absolute_import

from .textutils import get_tag_param
from .textutils import has_tag
from .parse_date import parse_date


class Query:
    pass


class SetOperation(Query):
    def __init__(self, left, operator, right):
        self.type = 'set operation'
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return '(<S> {} {} {} </S>)'.format(self.left, self.operator, self.right)

    def search(self, todos):
        left_side = list(self.left.search(todos))
        right_side = list(self.right.search(todos))
        if self.operator == 'union':
            for item in todos:
                if item in left_side or item in right_side:
                    yield item
        elif self.operator == 'intersect':
            for item in todos:
                if item in left_side and item in right_side:
                    yield item
        elif self.operator == 'except':
            for item in todos:
                if item in left_side and item not in right_side:
                    yield item


class ItemsPath(Query):
    def __init__(self, left, operator, right):
        self.type = 'items path'
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return '(<I> {} {} {} </I>)'.format(
            self.left if self.left else '',
            self.operator if self.operator else '',
            self.right
        )

    def search(self, todos):
        left_side = list(self.get_left_side(todos))
        for item in left_side:
            axes = list(self.get_axes_for_operator(item))
            for subitem in self.right.search(axes):
                yield subitem

    def get_left_side(self, todos):
        if self.left:
            return self.left.search(todos)
        # if self.operator in ('/', '/child::'):
        return [todos]
        # return list(todos)

    def get_axes_for_operator(self, todos):
        if self.operator in ('/', '/child::'):
            return todos.yield_children()
        elif self.operator in ('//', '/descendant::'):
            return todos.yield_descendants()
        elif self.operator in ('///', '/descendant-or-self::'):
            return todos.yield_descendants_and_self()
        elif self.operator == '/ancestor-or-self::':
            return todos.yield_ancestors_and_self()
        elif self.operator == '/ancestor::':
            return todos.yield_ancestors()
        elif self.operator == '/parent::':
            return todos.yield_parent()
        elif self.operator == '/following-sibling::':
            return todos.yield_following_siblings()
        elif self.operator == '/following::':
            return todos.yield_following()
        elif self.operator == '/preceding-sibling::':
            return todos.yield_preceding_siblings()
        elif self.operator == '/preceding::':
            return todos.yield_preceding()


class Slice(Query):
    def __init__(self, left, slice):
        self.type = 'slice'
        self.left = left
        self.slice = slice or ':'
        if slice and ':' not in slice:
            self.index = int(slice)
            self.slice_start = None
            self.slice_stop = None
        elif slice:
            self.index = None
            self.slice_start, self.slice_stop = [(int(i) if i else None) for i in slice.split(':')]

    def __str__(self):
        return '(<L>{} [{}]</L>)'.format(
            self.left, self.slice
        )

    def search(self, todos):
        left_side = list(self.left.search(todos))
        if self.slice == ':':
            for item in left_side:
                yield item
            return
        if self.index is not None:
            yield list(left_side)[self.index]
            return
        for item in list(left_side)[self.slice_start:self.slice_stop]:
            yield item


class MatchesQuery(Query):
    def search(self, todos):
        for item in todos:
            if self.matches(item):
                yield item


class BooleanExpression(MatchesQuery):
    def __init__(self, left, operator, right):
        self.type = 'boolean expression'
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return '(<B> {} {} {} </B>)'.format(
            self.left, self.operator, self.right
        )

    def matches(self, todoitem):
        matches_left = self.left.matches(todoitem)
        matches_right = self.right.matches(todoitem)
        if self.operator == 'and':
            return matches_left and matches_right
        elif self.operator == 'or':
            return matches_left or matches_right


class Unary(MatchesQuery):
    def __init__(self, operator, right):
        self.type = 'unary'
        self.operator = operator
        self.right = right

    def __str__(self):
        return '(<U> {} {} </U>)'.format(self.operator, self.right)

    def matches(self, todoitem):
        matches_right = self.right.matches(todoitem)
        return not matches_right


class Relation(MatchesQuery):
    def __init__(self, left, operator, right, modifier):
        self.type = 'relation'
        self.operator = operator
        self.left = left
        self.right = right
        self.modifier = modifier
        self.calculated_right = None

    def __str__(self):
        return '(<R> @{} {} [{}] {} </R>)'.format(
            self.left, self.operator, self.modifier, self.right
        )

    def matches(self, todoitem):
        if not todoitem:
            return False
        left_side = self.calculate_left_side(todoitem)
        right_side = self.calculate_right_side()
        if self.operator == '=':
            return left_side == right_side
        elif self.operator == '<=':
            return left_side <= right_side
        elif self.operator == '<':
            return left_side < right_side
        elif self.operator == '>':
            return left_side > right_side
        elif self.operator == '>=':
            return left_side >= right_side
        elif self.operator == '!=':
            return left_side != right_side
        elif self.operator == 'contains':
            return right_side in left_side
        elif self.operator == 'beginswith':
            return left_side.startswith(right_side)
        elif self.operator == 'endswith':
            return left_side.endswith(right_side)
        elif self.operator == 'matches':
            return re.match(right_side, left_side)

    def calculate_left_side(self, todoitem):
        if self.left.value == 'text':
            left = todoitem.get_text()
        elif self.left.value == 'id':
            left = todoitem.id()
        elif self.left.value == 'line':
            left = str(todoitem.get_line_number())
        elif self.left.value == 'type':
            left = todoitem.get_type()
        else:
            left = todoitem.get_tag_param(self.left.value)
        return self.apply_modifier(left)

    def calculate_right_side(self):
        if not self.calculated_right:
            self.calculated_right = self.apply_modifier(self.right.value)
        return self.calculated_right

    def apply_modifier(self, value):
        if not value:
            return value
        if self.modifier == 'i':
            return value.lower()
        elif self.modifier == 's':
            return value
        elif self.modifier == 'n':
            try:
                return int(value)
            except ValueError:
                return None
        elif self.modifier == 'd':
            return parse_date(value)


class Atom(MatchesQuery):
    def __init__(self, token):
        self.type = token.type
        self.value = token.value

    def __str__(self):
        return self.value

    def matches(self, todoitem):
        if self.type == 'attribute':
            return todoitem.has_tag(self.value)
        elif self.type == 'search term':
            return self.value in todoitem.get_text()
        else:
            return True
