from __future__ import absolute_import

from .textutils import get_tag_param
from .textutils import has_tag
from .parse_date import parse_date


class Query:
    def filter(self, todos):
        return todos.filter(lambda i: i.todoitem in [i.todoitem for i in self.search(todos)])


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
            return todos.search(lambda i: i in left_side or i in right_side)
        elif self.operator == 'intersect':
            return todos.search(lambda i: i in left_side and i in right_side)
        elif self.operator == 'except':
            return todos.search(lambda i: i in left_side and i not in right_side)


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
        if self.left:
            left_side = self.left.search(todos)
        else:
            left_side = [todos]
        for item in left_side:
            right_side = [i.todoitem for i in self.right.search(item)]
            for subitem in self.get_neighbours_for_operator(item):
                if subitem.todoitem in right_side:
                    yield subitem

    def get_neighbours_for_operator(self, todos):
        if self.operator in ('/', '/child::'):
            print('s', todos.subitems)
            print('g', todos.get_children().subitems)
            return todos.subitems
        elif self.operator in ('//', '/descendant::'):
            return todos.get_descendants()

        # if self.operator in ('///', '/descendant-or-self::'):
        # if self.operator == '/ancestor-or-self::':
        # if self.operator == '/ancestor::':
        # if self.operator == '/parent::':
        # if self.operator == '/following-sibling::':
        # if self.operator == '/following::':
        # if self.operator == '/preceding-sibling::':
        # if self.operator == '/preceding::':


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
            return left_side
        if self.index is not None:
            return list(left_side)[self.index]
        return list(left_side)[self.slice_start:self.slice_stop]


class MatchesQuery(Query):
    def filter(self, todos):
        return todos.filter(lambda i: self.matches(i))

    def search(self, todos):
        return todos.search(lambda i: self.matches(i))


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
        if not todoitem:
            return False
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
