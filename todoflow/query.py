from __future__ import absolute_import

from .textutils import get_tag_param
from .textutils import has_tag


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

    def filter(self, todos):
        left_todos = self.left.filter(todos)
        right_todos = self.right.filter(todos)
        if self.operator == 'union':
            return todos.filter(lambda i: i in left_todos or i in right_todos)
        elif self.operator == 'intersect':
            return todos.filter(lambda i: i in left_todos and i in right_todos)
        elif self.operator == 'except':
            return todos.filter(lambda i: i in left_todos and i not in right_todos)


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

    def filter(self, todos):
        if self.left:
            left_side = self.left.filter(todos)
        else:
            left_side = todos._todos_tree._children
        print('L', left_side)
        right_side = self.right.filter(todos)
        if self.operator in ('/', '/child::'):
            return right_side.filter(lambda i: i.get_parent()._value if i.get_parent() else None in left_side)
        if self.operator in ('//', '/descendant-or-self::'):
            return right_side.filter(lambda i: any(p in left_side for p in i.parents()))
        if self.operator in ('///', '/descendant::'):
            return right_side.filter(lambda i: i in left_size or any(p in left_side for p in i.parents()))
        if self.operator == '/ancestor-or-self::':
            return right_side.filter(lambda i: i in left_size or any(p in left_side for p in i.descendants()))
        if self.operator == '/ancestor::':
            return right_side.filter(lambda i: any(p in left_side for p in i.descendants()))
        if self.operator == '/parent::':
            return right_side.filter(lambda i: any(p in left_side for p in i.children))
        if self.operator == '/following-sibling::':
            return right_side.filter(lambda i: any(p in left_side for p in i.preceding_siblings()))
        if self.operator == '/following::':
            return right_side.filter(lambda i: any(p in left_side for p in i.preceding()))
        if self.operator == '/preceding-sibling::':
            return right_side.filter(lambda i: any(p in left_side for p in i.following_siblings()))
        if self.operator == '/preceding::':
            return right_side.filter(lambda i: any(p in left_side for p in i.following()))


class Slice(Query):
    def __init__(self, left, slice):
        self.type = 'slice'
        self.left = left
        self.slice = slice or ':'
        if slice and ':' not in slice:
            self.index = int(slice)
            self.slice_start = None
            self.slice_end = None
        elif slice:
            self.index = None
            self.slice_start, self.slice_end = [(int(i) if i else None) for i in slice.split(':')]

    def __str__(self):
        return '(<L>{} [{}]</L>)'.format(
            self.left, self.slice
        )

    def filter(self, todos):
        left_side = self.left.filter(todos)
        if self.slice == ':':
            return left_side
        elif not self.index is None:
            return left_side[self.index]
        else:
            return left_side[self.slice_start:self.slice_end]


class MatchesQuery(Query):
    def filter(self, todos):
        return todos.filter(lambda i: self.matches(i))


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
    def __init__(self, operator, expression):
        self.type = 'unary'
        self.operator = operator
        self.expression = expression

    def __str__(self):
        return '(<U> {} {} </U>)'.format(self.operator, self.expression)

    def matches(self, todoitem):
        matches_expression = expression.matches(todoitem)
        return not matches_expression


class Relation(MatchesQuery):
    def __init__(self, left, operator, right, modifier):
        self.type = 'relation'
        self.operator = operator
        self.left = left
        self.right = right
        self.calculated_right = None
        self.modifier = modifier

    def __str__(self):
        return '(<R> @{} {} [{}] {} </R>)'.format(
            self.left, self.operator, self.modifier, self.right
        )

    def matches(self, todoitem):
        left_side = self.calculate_left(todoitem)
        right_side = self.calculate_right()
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

    def calculate_left(self, todoitem):
        if self.left.value == 'text':
            left = todoitem.text()
        elif self.left.value == 'id':
            left = todoitem.id()
        elif self.left.value == 'line':
            left = todoitem.line_number()
        elif self.left.value == 'type':
            left = todoitem.type()
        else:
            left = todoitem.get_tag_param(self.left.value)
        return self.apply_modifier(left)

    def calculate_right(self):
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
            return self.value in todoitem.text
        else:
            return True
