# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re

from .query_lexer import QueryLexer
from .query import SetOperation
from .query import ItemsPath
from .query import Slice
from .query import MatchesQuery
from .query import BooleanExpression
from .query import Unary
from .query import Relation
from .query import Atom


def parse(text):
    return QueryParser().parse(text)


class QueryParserError(Exception):
    pass


class QueryParser:
    PRECEDENCE = {
        'except': 1,
        'intersect': 2,
        'union': 3,
        '/ancestor-or-self::': 5,
        '/ancestor::': 5,
        '/descendant-or-self::': 5,
        '/descendant::': 5,
        '/following-sibling::': 5,
        '/following::': 5,
        '/preceding-sibling::': 5,
        '/preceding::': 5,
        '/child::': 5,
        '/parent::': 5,
        '///': 5,
        '//': 5,
        '/': 5,
        'not': 7,
        'or': 10,
        'and': 11,
        '=': 20,
        '!=': 20,
        '<': 20,
        '>': 20,
        '<=': 20,
        '>=': 20,
        'contains': 20,
        'beginswith': 20,
        'endswith': 20,
        'matches': 20,
    }

    SET_OPERATORS = (
        'union', 'intersect', 'except',
    )

    ITEMS_PATH_OPERATORS = (
        '/ancestor-or-self::', '/ancestor::',
        '/descendant-or-self::', '/descendant::',
        '/following-sibling::', '/following::',
        '/preceding-sibling::', '/preceding::',
        '/child::', '/parent::',
        '///', '//', '/',
    )

    BOOLEAN_OPERATOS = (
        'and', 'or', 'not'
    )

    RELATION_OPERATORS = (
        '=', '!=', '<', '>', '<=', '>=',
        'contains', 'beginswith', 'endswith', 'matches',
    )

    def parse(self, text):
        self.text = text
        self.tokens = QueryLexer().tokenize(text)
        query = self.parse_set_operation(None, 0)
        return query

    def pick(self):
        try:
            return self.tokens[0]
        except IndexError:
            raise_parse('unexpected end')

    def pop(self):
        try:
            return self.tokens.pop(0)
        except IndexError:
            raise_parse('unexpected end')

    def pop_close(self):
        return self.pop()

    def pop_slice(self):
        return self.pop()

    def pop_not(self):
        return self.pop()

    def is_eof(self):
        return not self.tokens

    def is_operator(self):
        if self.is_eof():
            return False
        return self.pick().type == 'operator'

    def is_set_operator(self):
        return self.is_operator() and self.pick().value in QueryParser.SET_OPERATORS

    def is_boolean_operator(self):
        return self.is_operator() and self.pick().value in QueryParser.BOOLEAN_OPERATOS

    def is_relation_operator(self):
        return self.is_operator() and self.pick().value in QueryParser.RELATION_OPERATORS

    def is_items_path_operator(self):
        return self.is_operator() and self.pick().value in QueryParser.ITEMS_PATH_OPERATORS

    def is_slice(self):
        if self.is_eof():
            return False
        return self.pick().type == 'slice'

    def is_not(self):
        return self.is_operator() and self.pick().value == 'not'

    def is_atom(self):
        return self.pick().type in set([
            'attribute', 'wild card', 'search term'
        ])

    def is_open(self):
        if self.is_eof():
            return False
        token = self.pick()
        return token.type == 'punctuation' and token.value == '('

    def is_close(self):
        if self.is_eof():
            return False
        token = self.pick()
        return token.type == 'punctuation' and token.value == ')'

    def parse_set_operation(self, left, precedence):
        if not left:
            left = self.parse_items_path(None, 0)
        if self.is_set_operator():
            token = self.pick()
            current_precedence = QueryParser.PRECEDENCE[token.value]
            if current_precedence > precedence:
                self.pop()
                right = self.parse_set_operation(
                    None, current_precedence
                )
                return self.parse_set_operation(
                    SetOperation(left, token.value, right), precedence
                )
        return left

    def parse_items_path(self, left, precedence):
        slice = None
        if not left and self.is_items_path_operator():
            token = self.pop()
            current_precedence = QueryParser.PRECEDENCE[token.value]
            right = self.parse_items_path(None, current_precedence)
            return self.parse_items_path(
                ItemsPath(None, token.value, right), 0
            )
        if not left:
            left = self.parse_slice(None, 0)
        if self.is_items_path_operator():
            token = self.pick()
            current_precedence = QueryParser.PRECEDENCE[token.value]
            if current_precedence > precedence:
                self.pop()
                right = self.parse_items_path(None, current_precedence)
                if self.is_slice():
                    slice = self.pop().value
                return self.parse_items_path(
                    ItemsPath(left, token.value, right), precedence
                )
        return left

    def parse_slice(self, left, precedence):
        if not left:
            left = self.parse_boolean_expression(None, precedence)
        slice = None
        if self.is_slice():
            slice = self.pop().value
        return Slice(left, slice)

    def parse_boolean_expression(self, left, precedence):
        if not left:
            if self.is_not():
                self.pop_not()
                left = Unary('not', self.parse_relation(None, 0))
            else:
                left = self.parse_relation(None, 0)
        if self.is_boolean_operator():
            token = self.pick()
            current_precedence = QueryParser.PRECEDENCE[token.value]
            if current_precedence > precedence:
                self.pop()
                right = self.parse_boolean_expression(self.parse_relation(None, 0), current_precedence)
                return self.parse_boolean_expression(
                    BooleanExpression(left, token.value, right), precedence
                )
        return left

    def parse_relation(self, left, precedence):
        if self.is_not():
            self.pop()
            return Unary('not', self.parse_relation(None, 0))
        if not left:
            left = self.parse_atom()
        if self.is_relation_operator():
            operator = self.pop().value
            modifier = self.pop().value
            right = self.parse_atom()
            return Relation(left, operator, right, modifier)
        return left

    def parse_atom(self):
        if self.is_open():
            return self.parse_parenthesises()
        return Atom(self.pop())

    def parse_parenthesises(self):
        self.pop()
        result = self.parse_relation(None, 0)
        if not self.is_close():
            result = self.parse_boolean_expression(result, 0)
        if not self.is_close():
            result = self.parse_slice(result, 0)
        if not self.is_close():
            result = self.parse_items_path(result, 0)
        if not self.is_close():
            result = self.parse_set_operation(result, 0)
        self.pop_close()
        return result


def raise_parse(text, message=None):
    raise QueryParserError(
        "can't parse - {}{}".format(text, ': ' + message if message else '')
    )
