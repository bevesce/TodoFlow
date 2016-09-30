# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import inspect

from ply import lex
from ply import yacc

from .query import AndQuery
from .query import LinenumOpQuery
from .query import NotQuery
from .query import OnlyFirst
from .query import OrQuery
from .query import PlusDescendants
from .query import ProjectOpQuery
from .query import SourceOpQuery
from .query import SubstringQuery
from .query import TagOpQuery
from .query import TagQuery
from .query import TypeOpQuery
from .query import UniqueidOpQuery

from .config import tag_indicator

tokens = (
    'LPAREN', 'RPAREN',
    'AND', 'OR', 'NOT',
    'EQ', 'LEQ', 'GEQ', 'NEQ', 'GE', 'LE', 'IN', 'CONTAINS', 'MATCHES',
    'PLUS_DESCENDANTS', 'ONLY_FIRST',
    'TEXT', 'TAG', 'PROJECT', 'TYPE', 'UNIQUEID', 'LINENUM', 'SOURCE'
)

# t_TAG_INDICATOR = r'@'
t_LPAREN = r'\('
t_RPAREN = r'\)'
# t_QUOTE = r'"'
t_TAG = tag_indicator + r'[^\s)]*'
r_PROJECT = ':|project'
t_ignore = ' \t\n\r'
r_ignore = r'(?<!\\)"'
t_EQ = r'='
t_LEQ = r'<='
t_LE = r'<'
t_GE = r'>'
t_GEQ = r'>='
r_NEQ = r'!='
r_IN = r'->'
r_CONTAINS = r'<-'
r_MATCHES = r'~'
r_PLUS_DESCENDANTS = r'\+d'
r_ONLY_FIRST = r'\+f'
r_TYPE = r'type'
t_UNIQUEID = 'uniqueid'
t_LINENUM = 'linenum'
t_SOURCE = 'source'


def t_error(token):
    print("Illegal character '%s'" % token.value[0])
    token.lexer.skip(1)


reserved = {
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR',
    '=': 'EQ',
    '<=': 'LEQ',
    '<': 'LE',
    '>': 'GE',
    '>=': 'GEQ',
    '!=': 'NEQ',
    '->': 'IN',
    '<-': 'CONTAINS',
    '+d': 'PLUS_DESCENDANTS',
    '+f': 'ONLY_FIRST',
    ':': 'PROJECT',
    'project': 'PROJECT',
    'type': 'TYPE',
    'uniqueid': 'UNIQUEID',
    'linenum': 'LINENUM',
    'source': 'SOURCE',
}


def t_TEXT(t):
    r'[^\s@\(\)][^\s\(\)]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t


def p_E1_and(p):
    'E1 : E1 AND E2'
    p[0] = AndQuery(p[1], p[3])


def p_E1_plus_d(p):
    'E1 : E2 PLUS_DESCENDANTS'
    p[0] = PlusDescendants(p[1])


def p_E1_only_f(p):
    'E1 : E2 ONLY_FIRST'
    p[0] = OnlyFirst(p[1])


def p_E1_E2(p):
    'E1 : E2'
    p[0] = p[1]


def p_E2_or(p):
    'E2 : E2 OR E3'
    p[0] = OrQuery(p[1], p[3])


def p_E2_E3(p):
    'E2 : E3'
    p[0] = p[1]


def p_E3_not(p):
    'E3 : NOT E3'
    p[0] = NotQuery(p[2])


def p_E3_E4(p):
    'E3 : E4'
    p[0] = p[1]


def p_E4_tag(p):
    'E4 : TAG'
    p[0] = TagQuery(p[1])


def p_E4_paren(p):
    'E4 : LPAREN E1 RPAREN'
    p[0] = p[2]


def p_E4_words(p):
    'E4 : words'
    p[0] = SubstringQuery(p[1].strip())


def p_E4_argument_operator_words(p):
    'E4 : argument operator words'
    p[1].operation = p[2]
    p[1].right_side = p[3].strip()
    p[0] = p[1]


def p_argument_tag(p):
    'argument : TAG'
    p[0] = TagOpQuery(p[1])


def p_argument_project(p):
    'argument : PROJECT'
    p[0] = ProjectOpQuery()


def p_argument_type(p):
    'argument : TYPE'
    p[0] = TypeOpQuery()


def p_argument_uniqueid(p):
    'argument : UNIQUEID'
    p[0] = UniqueidOpQuery()


def p_argument_linenum(p):
    'argument : LINENUM'
    p[0] = LinenumOpQuery()


def p_argument_source(p):
    'argument : SOURCE'
    p[0] = SourceOpQuery()


def p_operator_eq(p):
    'operator : EQ'
    p[0] = lambda a, b: a == b


def p_operator_neq(p):
    'operator : NEQ'
    p[0] = lambda a, b: a != b


def p_operator_qeq(p):
    'operator : GEQ'
    p[0] = lambda a, b: a >= b


def p_operator_leq(p):
    'operator : LEQ'
    p[0] = lambda a, b: a <= b


def p_operator_le(p):
    'operator : LE'
    p[0] = lambda a, b: a < b


def p_operator_ge(p):
    'operator : GE'
    p[0] = lambda a, b: a > b


def p_operator_in(p):
    'operator : IN'
    p[0] = lambda a, b: a in b


def p_operator_contains(p):
    'operator : CONTAINS'
    p[0] = lambda a, b: b in a


def p_operator_matches(p):
    'operator : MATCHES'
    import re
    p[0] = lambda a, b: re.match(b, a)


def p_words(p):
    'words : TEXT words'
    p[0] = p[1].replace('"', '') + ' ' + p[2]


def p_words_epsilon(p):
    'words : '
    p[0] = ''


def p_error(p):
    print("Syntax error in input!!!")
    print(p)
    print('_')


def _get_pickle_path():
    return os.path.expanduser('~/.todoflow_parsetab.pickle')

lex.lex()
_parser = yacc.yacc(
    debug=0, write_tables=0
)


class Parser(object):
    def __init__(self):
        self.parser = _parser

    def parse(self, text):
        return self.parser.parse(text)


def parse(text_or_query):
    try:
        query = _parser.parse(text_or_query)
        return query
    except TypeError:
        return text_or_query
