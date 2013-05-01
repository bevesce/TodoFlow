# -*- coding: utf-8 -*-
#
# Configuration of topy
#
# You should read README first
#
from seamless_dropbox import open
from datetime import date
import re
import console
import webbrowser
# File that stores path to your todo lists
# This location keeps up with alfred workflow
# best practices but you can change it
# to wherever you want
files_list_path = '/Users/bvsc/Dropbox/TODO/'
files_list_name = 'lists'

# logical operator to join shortened queries
quick_query_abbreviations_conjuction = ' and '  # ' or '

# fill with your own, this is what I use:
quick_query_abbreviations = {
    't': '@today',
    'n': '@next',
    'd': 'not @done',
    'u': '@due',
    's': 'project = Studia',
    'i': 'index = 0',
    'f': '(@today or @next)',
    'q': 'project = Projects and not project = Archive'
}

# add date value when tagging with @done
date_after_done = True

# include project titles in list displayed by alfred
# when searching with `q` keyword
include_project_title_in_alfred = False

# when generating html items are given classes
# define how many different classes (depengin on identation level)
# you want to have
number_of_css_classes = 4

# symbols on icons can be transparent or white
white_symbols_on_icons = False  # True

#################################################
# todolist_utils

"""
Module provides functions used by objects in todolist module,
mostly operations on text.
"""

def set_font(color=(0.00, 0.00, 0.00), size=18, font='dejavusansmono'):
	console.set_font(font, size)
	console.set_color(color)

def set_size(size):
	console.set_font('dejavusansmono', size)

def set_color(c):
	console.set_color(*c)

ctoday = (0.00, 0.50, 0.50)
cnext = (0.00, 0.25, 0.50)
cdue = (1.00, 0.00, 0.50)
cdone = (0.70, 0.70, 0.70)
cnote = (0.30, 0.30, 0.30)
ctask = (0.10, 0.10, 0.10)

# regexpes used in functions:

# ( everything but `)` ) or lookahead for \s or end of line
tag_param_regexp = r'(\(([^)]*)\)|(?=(\s|$)))'
# prepend word (sequence without \s and `(`)
tag_regexp_without_at = r'[^\(\s]*' + tag_param_regexp
tag_pattern_without_at = re.compile(tag_regexp_without_at + r'\Z')
# prepend '@'
tag_pattern = re.compile('(@' + tag_regexp_without_at + ')')

#


def custom_tag_regexp(tag):
    return re.compile('@' + tag + tag_param_regexp)

custom_tag_regexp.param_group = 2
done_tag = custom_tag_regexp('done')


def add_tag_to_text(text, tag, param=None):
    if text[-1] != ' ':
        text += ' '
    text += "@" + tag
    if param:
        text += '({0})'.format(param)
    return text


def get_tag_param(text, tag):
    match = re.search(custom_tag_regexp(tag), text)
    if match:
        return match.group(custom_tag_regexp.param_group)
    return None


def remove_trailing_tags(line):
    sp = re.split('\s@', line)
    idx = len(sp) - 1
    while tag_pattern_without_at.match(sp[idx].strip()):
        idx -= 1
        if idx <= 0:
            break
    idx = max(1, idx + 1)  # don't want empty lines, also, loops goes 1 too far
    return ' @'.join(sp[0:idx])


def extract_content(typ, line):
    text = extract_text(typ, line)
    if typ in ('task', 'note'):
        return remove_trailing_tags(text)
    elif typ == 'project':
        splitted = text.split(':')
        return ':'.join(splitted[0:-1])


def extract_text(typ, line):
    stripped = line.strip()
    if typ == 'task':
        return stripped[2:]
    return stripped


def enclose_tags(text, prefix, postfix):
    """
    puts `prefix` before and `postfix` after
    every tag in text
    """
    def f(t):
        return prefix + t.group(1) + postfix
    return re.sub(tag_pattern, f, text)


def remove_tag_from_text(text, tag):
    # TODO: lefts two spaces, maybe fix someday
    tag_pattern = custom_tag_regexp(tag)
    return re.sub(tag_pattern, '', text)


def date_to_countdown(date_iso):
    """
    date should be string formated as in ISO format,
    returns number of days from `date_iso` to today
    as string, when can't calculate this number
    returns `???`
    """
    number_of_digits = 3
    # nice formatting for due dates up to 2,74 years in the future
    try:
        splitted = [int(x) for x in date_iso.split('-')]
        param_date = date(splitted[0], splitted[1], splitted[2])
        today = date.today()
        countdown = str((param_date - today).days)
        return countdown.zfill(number_of_digits)
    except Exception as e:
        # print e
        return '?' * number_of_digits


# todolist_utils
#################################################
# todolist_lexer

"""
# Lexer of todo lists.

Token stores its type in string, posible types are:

* $ - end of input
* indent - indentation
* newline - `\n`
* dedent - end of indented text
* task - line tht begins with `\t*- `
* project-title - line that is not task and ends with `:`
(with eventual trailing tags after `:`)
* note - line that is not task or project-title

"""


class Token(object):
    @staticmethod
    def is_task(line):
        return line.strip()[0:2] == '- '

    tag_pattern_without_at = re.compile(r'[^\(\s]*(|\([^)]*\))')
    # defines what can be *after @*
    # Tag -> @ Word | @ Word ( Words ) .
    #
    # first part of regexp defines Word -
    # ensures that there is no white signs and `(` in it
    #
    # second part of regexp defines epsilon | ( Words ) -
    # nothing or `(` everything but `)` followed by `)`
    #

    @staticmethod
    def is_project(line):
        splitted = line.split(':')
        if len(splitted) < 2:  # no `:` in line
            return False
        if line[-1] == ' ':  # trailing space after `:`
            return False
        if splitted[1].strip() != '' and splitted[1][0] != '@':
            return False
        # only tags are allowed after `:`
        after_colon = splitted[-1].split('@')
        only_tags_after_colon = all([
            Token.tag_pattern_without_at.match(tag) for tag in after_colon
        ])
        return only_tags_after_colon

    def __init__(self, line=None, indent_level=0, line_no=0):
        if line:
            self.indent_level = indent_level
            self.line_no = line_no
            self.text = line

            if Token.is_task(line):
                self.type = 'task'
            elif Token.is_project(line):
                self.type = 'project-title'
            else:
                self.type = 'note'
        else:  # if there's no line it's end of input
            self.type = '$'
            self.text = ''


class Dedent(Token):
    def __init__(self):
        self.type = 'dedent'
        self.text = ''


class Indent(Token):
    def __init__(self):
        self.type = 'indent'
        self.text = ''


class NewLine(Token):
    def __init__(self):
        self.type = 'newline'
        self.text = '\n'


class Lexer(object):
    def __init__(self, lines):
        self.tokens = Lexer.tokenize(lines)

    @staticmethod
    def indent_level(text):
        indent_char = '\t'
        level = 0
        while level < len(text) and text[level] == indent_char:
            level += 1
        return level

    @staticmethod
    def tokenize(lines):
        """turns input into tokens"""
        tokens = []
        indent_levels = [0]
        for line_no, line in enumerate(lines):
            if line == '':
                tokens.append(NewLine())
                # empty lines are ignored in
                # flow of indents so
                continue

            # generate indent and dedent tokens
            current_level = Lexer.indent_level(line)
            if current_level > indent_levels[-1]:
                indent_levels.append(current_level)
                tokens.append(Indent())
            elif current_level < indent_levels[-1]:
                while current_level < indent_levels[-1]:
                    indent_levels.pop()
                    tokens.append(Dedent())

            tokens.append(Token(line, current_level, line_no))

        # add $ token at the end and return
        return [Token()] + tokens[::-1]

    def top(self):
        """returns token on top of stack"""
        return self.tokens[-1]

    def pop(self):
        """removes token from top of stack and returns it"""
        return self.tokens.pop()

    def consume(self, expected_type):
        """removes token from top of stack
        and raises ParseError if it's not of expected type"""
        if self.tokens.pop().type != expected_type:
            raise ParseError


class ParseError(Exception):
    pass

# todolist_lexer
#################################################
# filterpredicate


"""
Predicates for filtering todo list.
Module defines lexer, parser and predicates themself.

Predicate implements method test(text) that returns if
predicate applies to given text.

For example '@today and not @done' returns if text contains
tag @today and not contains tag @done.

grammar of predicates (SLR(1)):

S     -> E1 | E1 +d
E1    -> E1 and E2
       | E2.
E2    -> E2 or E3
       | E3.
E3    -> not E3
       | E4
       | ( E1 ).
E4    -> Argument op Words
       | Words
       | Tag .
Words -> word Words
       | .

those rules are not part of SLR automaton:
op     -> = | != | < | <= | >= | > | matches | contains | $ . ($ is abbreviation for contains)
Tag    -> @ word | EndTag.
EndTag -> (Words) | epsilon.
Argument -> project | line | uniqueid | content | type | level | parent | index | Tag.



Arguments:
- project - check project title
- line - line with whole `-`, and tags
- uniqueid - id of element
- content - line without formatting and trailing tags
- type - "project", task or note
- level - indentation level
- parent - checks parents recursively
- index - index in sublist, starts with 0
- tag parameter - value enclosed in parenthesises after tag
"""


class TokenF(object):
    operators = ['=', '!=', '<', '<=', '>', '>=', '$', 'matches', 'contains']
    log_ops = ['and', 'or', 'not']
    keywords = ['project', 'line', 'uniqueid', 'content', 'type', 'level', 'parent', 'index']
    tag_prefix = '@'

    def __init__(self, text=None):
        # long switch-case / if:elif chain
        self.text = text
        # set type of token
        if not text:
            self.type = '$'
        elif text in TokenF.operators:
            self.type = 'op'
        elif text == '+d':
            self.type = 'plusD'
        elif text in TokenF.log_ops:
            self.type = text
        elif text in TokenF.keywords:
            self.type = 'arg'
        elif text[0] == TokenF.tag_prefix:
            self.type = 'tag'
        elif text[0] == '"':
            self.type = 'word'
            self.text = text[1:-1]
        elif text == '(':
            self.type = 'lparen'
        elif text == ')':
            self.type = 'rparen'
        else:
            self.type = 'word'

    def __str__(self):
        return repr(self.text) + ' : ' + self.type


class LexerF(object):
    def __init__(self, input_text):
        self.tokens = LexerF.tokenize(input_text)

    @staticmethod
    def tokenize(input_text):
        """converts input text to list of tokens"""
        tokens = []

        def add_token(text=None):
            if text != '' and text != ' ':
                tokens.append(TokenF(text))

        idx = 0
        collected = ''
        text_length = len(input_text)

        while idx < text_length + 1:
            # lengthy switch-case like statement
            # that processes input text depending on
            # current char
            if idx == text_length:
                # finish tokenizing
                add_token(collected)  # add remaining collected text
                add_token()  # add end of input token
            elif input_text[idx] == '+':
                if idx + 1 < len(input_text):
                    if input_text[idx + 1] == 'd':
                        add_token(collected)
                        collected = ''
                        add_token('+d')
                        idx += 1
            elif input_text[idx] == ' ':
                # spaces separate but but don't have semantic meaning
                add_token(collected)
                collected = ''
            elif input_text[idx] in ('(', ')'):
                # parenthesises seperate
                add_token(collected)
                collected = ''
                add_token(input_text[idx])
            elif input_text[idx] in ('<', '>', '!'):
                # operators or prefixes of operators
                add_token(collected)
                collected = input_text[idx]
            elif input_text[idx] == '=':
                if collected in ('<', '>', '!'):
                    # "="" preceded by any of this signs is an operator
                    collected += '='
                    add_token(collected)
                else:
                    # "=" by itself is also an operator
                    add_token(collected)
                    add_token('=')
                collected = ''
            elif input_text[idx] == '$':
                add_token(collected)
                add_token('$')
                collected = ''
            elif input_text[idx] == '"':
                # quoted part of input is allways a word
                add_token(collected)
                collected = ''
                next_quotation_mark_idx = input_text.find('"', idx + 1)
                if next_quotation_mark_idx == -1:
                    # when there is no matching quotation mark
                    # end of the input is assumed
                    add_token(input_text[idx:] + '"')
                    idx = text_length - 1  # sets idx to that value so loop finishes in next iteration
                else:
                    add_token(input_text[idx:next_quotation_mark_idx + 1])
                    idx = next_quotation_mark_idx

            else:
                if collected in ('<', '>'):
                    add_token(collected)
                    collected = ''
                collected += input_text[idx]
            idx += 1

        return tokens[::-1]

    def pop(self):
        """pops and returns topmost token"""
        try:
            return self.tokens.pop()
        except IndexError:
            raise ParsingError

    def top(self):
        """returns topmost token"""
        try:
            return self.tokens[-1]
        except IndexError:
            raise ParsingError


class ParsingError(Exception):
    pass


class ParserF(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.create_parsing_table()
        self.stack = [0]

    def goto(self, state):
        self.parsing_table[self.stack[-2]][state]()

    def create_parsing_table(self):
        # long functions with declaration of parsing table and parser actions

        def shift_gen(state_no):
            def shift():
                """puts lexem and state number on stack"""
                self.stack.append(self.lexer.pop())
                self.stack.append(state_no)
            return shift

        def goto_gen(state_no):
            def goto():
                """puts state number on stack"""
                self.stack.append(state_no)
            return goto

        def err():
            raise ParsingError

        def acc():
            """returns abstrac syntax tree"""
            self.stack.pop()
            return self.stack[-1]

        # reductions, name of the functions contains information about production
        # -> is changed to __, terminals and nonterminals are separated by _
        # left side of production is preceded by `r`

        def rS__E1():
            self.stack.pop()
            self.goto('S')

        def rS__E1_plusD():
            self.stack.pop()
            self.stack.pop()  # +d

            self.stack.pop()
            e1 = self.stack.pop()
            self.stack.append(PlusDescendants(e1))
            self.goto('S')

        def rE3__E4():
            self.stack.pop()
            self.goto('E3')

        def rE1__E2():
            self.stack.pop()
            self.goto('E1')

        def rE2__E3():
            self.stack.pop()
            self.goto('E2')

        def rE3__lparen_E1_rparen():
            self.stack.pop()  # )
            self.stack.pop()

            self.stack.pop()
            e1 = self.stack.pop()

            self.stack.pop()  # (
            self.stack.pop()

            self.stack.append(e1)
            self.goto('E3')

        def rE2__E2_or_E3():
            self.stack.pop()
            e3 = self.stack.pop()

            self.stack.pop()  # or
            self.stack.pop()

            self.stack.pop()
            e2 = self.stack.pop()

            self.stack.append(OrPredicate(e2, e3))
            self.goto('E2')

        def rE4__Words():
            self.stack.pop()
            self.goto('E4')

        def rE1__E1_and_E2():
            self.stack.pop()
            e2 = self.stack.pop()

            self.stack.pop()  # and
            self.stack.pop()

            self.stack.pop()
            e1 = self.stack.pop()

            self.stack.append(AndPredicate(e1, e2))
            self.goto('E1')

        def rE3__not_E3():
            self.stack.pop()
            e3 = self.stack.pop()

            self.stack.pop()  # not
            self.stack.pop()

            self.stack.append(NotPredicate(e3))
            self.goto('E3')

        def rWords__epsilon():
            self.stack.append(WordsPredicate())
            self.goto('Words')

        def rE4__tag_op_Words():
            self.stack.pop()
            words = self.stack.pop()

            self.stack.pop()
            op = self.stack.pop()

            self.stack.pop()
            arg = self.stack.pop()

            self.stack.append(ArgOpPredicate(arg, words, op))
            self.goto('E4')

        def rE4__arg_op_Words():
            self.stack.pop()
            words = self.stack.pop()

            self.stack.pop()
            op = self.stack.pop()

            self.stack.pop()
            arg = self.stack.pop()

            self.stack.append(ArgOpPredicate(arg, words, op))
            self.goto('E4')

        def rWords__word_Words():
            self.stack.pop()
            words = self.stack.pop()

            self.stack.pop()
            word = self.stack.pop()

            self.stack.append(WordsPredicate(word) + words)
            self.goto('Words')

        def rE4__tag():
            self.stack.pop()
            tag = self.stack.pop()

            self.stack.append(TagPredicate(tag))
            self.goto('E4')

        # generated code
        self.parsing_table = {
            0: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": shift_gen(10),
                "op": err,
                "arg": shift_gen(9),
                "rparen": rWords__epsilon,
                "lparen": shift_gen(8),
                "not": shift_gen(7),
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": goto_gen(6),
                "E2": goto_gen(5),
                "E3": goto_gen(4),
                "E1": goto_gen(3),
                "E4": goto_gen(2),
                "Words": goto_gen(1),
            },
            1: {
                "$": rE4__Words,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE4__Words,
                "lparen": err,
                "not": err,
                "or": rE4__Words,
                "and": rE4__Words,
                "plusD": rE4__Words,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            2: {
                "$": rE3__E4,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE3__E4,
                "lparen": err,
                "not": err,
                "or": rE3__E4,
                "and": rE3__E4,
                "plusD": rE3__E4,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            3: {
                "$": rS__E1,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": err,
                "lparen": err,
                "not": err,
                "or": err,
                "and": shift_gen(19),
                "plusD": shift_gen(18),
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            4: {
                "$": rE2__E3,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE2__E3,
                "lparen": err,
                "not": err,
                "or": rE2__E3,
                "and": rE2__E3,
                "plusD": rE2__E3,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            5: {
                "$": rE1__E2,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE1__E2,
                "lparen": err,
                "not": err,
                "or": shift_gen(17),
                "and": rE1__E2,
                "plusD": rE1__E2,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            6: {
                "$": acc,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": err,
                "lparen": err,
                "not": err,
                "or": err,
                "and": err,
                "plusD": err,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            7: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": shift_gen(10),
                "op": err,
                "arg": shift_gen(9),
                "rparen": rWords__epsilon,
                "lparen": shift_gen(8),
                "not": shift_gen(7),
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": err,
                "E3": goto_gen(16),
                "E1": err,
                "E4": goto_gen(2),
                "Words": goto_gen(1),
            },
            8: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": shift_gen(10),
                "op": err,
                "arg": shift_gen(9),
                "rparen": rWords__epsilon,
                "lparen": shift_gen(8),
                "not": shift_gen(7),
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": goto_gen(5),
                "E3": goto_gen(4),
                "E1": goto_gen(15),
                "E4": goto_gen(2),
                "Words": goto_gen(1),
            },
            9: {
                "$": err,
                "word": err,
                "tag": err,
                "op": shift_gen(14),
                "arg": err,
                "rparen": err,
                "lparen": err,
                "not": err,
                "or": err,
                "and": err,
                "plusD": err,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            10: {
                "$": rE4__tag,
                "word": err,
                "tag": err,
                "op": shift_gen(13),
                "arg": err,
                "rparen": rE4__tag,
                "lparen": err,
                "not": err,
                "or": rE4__tag,
                "and": rE4__tag,
                "plusD": rE4__tag,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            11: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rWords__epsilon,
                "lparen": err,
                "not": err,
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": goto_gen(12),
            },
            12: {
                "$": rWords__word_Words,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rWords__word_Words,
                "lparen": err,
                "not": err,
                "or": rWords__word_Words,
                "and": rWords__word_Words,
                "plusD": rWords__word_Words,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            13: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rWords__epsilon,
                "lparen": err,
                "not": err,
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": goto_gen(24),
            },
            14: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rWords__epsilon,
                "lparen": err,
                "not": err,
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": goto_gen(23),
            },
            15: {
                "$": err,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": shift_gen(22),
                "lparen": err,
                "not": err,
                "or": err,
                "and": shift_gen(19),
                "plusD": err,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            16: {
                "$": rE3__not_E3,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE3__not_E3,
                "lparen": err,
                "not": err,
                "or": rE3__not_E3,
                "and": rE3__not_E3,
                "plusD": rE3__not_E3,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            17: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": shift_gen(10),
                "op": err,
                "arg": shift_gen(9),
                "rparen": rWords__epsilon,
                "lparen": shift_gen(8),
                "not": shift_gen(7),
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": err,
                "E3": goto_gen(21),
                "E1": err,
                "E4": goto_gen(2),
                "Words": goto_gen(1),
            },
            18: {
                "$": rS__E1_plusD,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": err,
                "lparen": err,
                "not": err,
                "or": err,
                "and": err,
                "plusD": err,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            19: {
                "$": rWords__epsilon,
                "word": shift_gen(11),
                "tag": shift_gen(10),
                "op": err,
                "arg": shift_gen(9),
                "rparen": rWords__epsilon,
                "lparen": shift_gen(8),
                "not": shift_gen(7),
                "or": rWords__epsilon,
                "and": rWords__epsilon,
                "plusD": rWords__epsilon,
                "S": err,
                "E2": goto_gen(20),
                "E3": goto_gen(4),
                "E1": err,
                "E4": goto_gen(2),
                "Words": goto_gen(1),
            },
            20: {
                "$": rE1__E1_and_E2,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE1__E1_and_E2,
                "lparen": err,
                "not": err,
                "or": shift_gen(17),
                "and": rE1__E1_and_E2,
                "plusD": rE1__E1_and_E2,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            21: {
                "$": rE2__E2_or_E3,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE2__E2_or_E3,
                "lparen": err,
                "not": err,
                "or": rE2__E2_or_E3,
                "and": rE2__E2_or_E3,
                "plusD": rE2__E2_or_E3,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            22: {
                "$": rE3__lparen_E1_rparen,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE3__lparen_E1_rparen,
                "lparen": err,
                "not": err,
                "or": rE3__lparen_E1_rparen,
                "and": rE3__lparen_E1_rparen,
                "plusD": rE3__lparen_E1_rparen,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            23: {
                "$": rE4__arg_op_Words,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE4__arg_op_Words,
                "lparen": err,
                "not": err,
                "or": rE4__arg_op_Words,
                "and": rE4__arg_op_Words,
                "plusD": rE4__arg_op_Words,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
            24: {
                "$": rE4__tag_op_Words,
                "word": err,
                "tag": err,
                "op": err,
                "arg": err,
                "rparen": rE4__tag_op_Words,
                "lparen": err,
                "not": err,
                "or": rE4__tag_op_Words,
                "and": rE4__tag_op_Words,
                "plusD": rE4__tag_op_Words,
                "S": err,
                "E2": err,
                "E3": err,
                "E1": err,
                "E4": err,
                "Words": err,
            },
        }

    def parse(self):
        """returns parsed predicate, throws ParsingError"""
        lex = self.lexer.top()
        state = self.stack[-1]
        parsed = self.parsing_table[state][lex.type]()
        if parsed:
            return parsed
        else:
            return self.parse()


class OrPredicate(object):
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side

    def test(self, item):
        return self.left_side.test(item) or self.right_side.test(item)

    def __str__(self):
        return "{0} or {1}".format(self.left_side, self.right_side)


class AndPredicate(object):
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side

    def test(self, item):
        return self.left_side.test(item) and self.right_side.test(item)

    def __str__(self):
        return "{0} and {1}".format(self.left_side, self.right_side)


class NotPredicate(object):
    def __init__(self, negated):
        self.negated = negated

    def test(self, item):
        return not self.negated.test(item)

    def __str__(self):
        return "not {0}".format(self.negated)

# all operation are case insensitive
op_functions = {
    '=': lambda x, y: x.lower() == y.lower(),
    '!=': lambda x, y: x.lower() != y.lower(),
    '<': lambda x, y: x.lower() < y.lower(),
    '<=': lambda x, y: x.lower() <= y.lower(),
    '>=': lambda x, y: x.lower() >= y.lower(),
    '>': lambda x, y: x.lower() > y.lower(),
    '$': lambda x, y: y.lower() in x.lower(),
    'matches': lambda x, y: bool(re.match(y, x))
}

op_functions['contains'] = op_functions['$']


class ArgOpPredicate(object):
    def __init__(self, left_side, right_side, op):
        self.left_side = left_side.text
        self.right_side = right_side.words
        self.op = op.text

    def test(self, item):
        # long switch-case / if:elif chain
        # runs different tests depending on self.left_side
        if self.left_side[0] == '@':
            tag_search = '(^|(?<=\s))' + self.left_side + r'\(([^)]*)\)'
            match = re.search(tag_search, item.title.text)
            if match:
                left_side = match.group(2)
            else:
                return False
            r = op_functions[self.op](left_side, self.right_side)
            return r

        elif self.left_side == 'project':
            projects_meets = []
            # if item itself is a project it must be considered
            if item.type == 'project':
                if op_functions[self.op](item.title.content, self.right_side):
                    projects_meets.append(True)
                else:
                    projects_meets.append(False)
            # check chain of parents
            while item.parent_item:
                if (op_functions[self.op](item.parent_item.title.content, self.right_side) and \
                   item.parent_item.type == 'project'):
                    projects_meets.append(True)
                else:
                    projects_meets.append(False)
                item = item.parent_item

            if self.op == '!=':  # != behaves in other way
                return all(projects_meets)
            else:
                return any(projects_meets)

        elif self.left_side == 'line':
            return op_functions[self.op](item.title.line.strip(), self.right_side.strip())
        elif self.left_side == 'uniqueid':
            return op_functions[self.op](str(item.title._id), self.right_side)
        elif self.left_side == 'content':
            return op_functions[self.op](item.title.content, self.right_side)
        elif self.left_side == 'type':
            return op_functions[self.op](item.type, self.right_side)
        elif self.left_side == 'level':
            return op_functions[self.op](str(item.title.indent_level), self.right_side)
        elif self.left_side == 'parent':
            if item.parent_item:
                return op_functions[self.op](item.parent_item.title.content, self.right_side)
            return False
        elif self.left_side == 'index':
            return op_functions[self.op](str(item.index()), self.right_side)

    def __str__(self):
        return "{0} {2} {1}".format(self.left_side, self.right_side, self.op)


class PlusDescendants(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def test(self, item):
        # if predicate is true for any parent it's also true for self
        while item:
            if self.predicate.test(item):
                return True
            item = item.parent_item
        return False

    def str(self):
        return str(self.predicate) + ' +d'


class WordsPredicate(object):
    """if text contains some text as subtext"""
    def __init__(self, words=None):
        self.words = words.text if words else ''

    def test(self, item):
        return self.words.lower() in item.title.text.lower()

    def __str__(self):
        return self.words

    def __add__(self, other):
        new_word = WordsPredicate()
        new_word.words = (self.words + ' ' + other.words).strip()
        return new_word


class TagPredicate(object):
    def __init__(self, tag):
        self.tag = tag.text

    def test(self, item):
        return item.has_tag(self.tag)

    def __str__(self):
        return self.tag


def parse_predicate(text):
    return ParserF(LexerF(text)).parse()

# filterpredicate
#################################################
# todolist
"""
Module defines main objects of todolist structure:
- TodoList
- Item
- Task
- Project
- Note
- NewLineItem

"""

from cgi import escape


class TodoList(object):
    items_by_id = {}
    _current_id = 0

    @classmethod
    def assign_id(cls, item):
        cls.items_by_id[cls._current_id] = item
        cls._current_id += 1
        return cls._current_id - 1

    @classmethod
    def tag(cls, id_no, tag, param=None):
        cls.items_by_id[id_no].tag(tag, param)

    @classmethod
    def do(cls, id_no):
        cls.items_by_id[id_no].tag(
            'done',
            date.today().isoformat() if date_after_done else None
        )

    @classmethod
    def get_item(cls, id_no):
        return cls.items_by_id[id_no]

    @classmethod
    def get_content(cls, id_no):
        return cls.items_by_id[id_no].get_content()

    @classmethod
    def remove(cls, id_no):
        cls.items_by_id[id_no].remove_self_from_parent()

    def __init__(self, items=None):
        self.items = items if items else []
        self.set_parent_list(self.items)
        self.source = None

    def __str__(self):
        return self.as_plain_text()

    def __nonzero__(self):
        return bool(self.items)

    def __add__(self, other):
        items = self.items

        first_trailing_newline_idx = len(items) - 1
        while first_trailing_newline_idx > 0 and\
              isinstance(items[first_trailing_newline_idx], NewLineItem):
            first_trailing_newline_idx -= 1
        first_trailing_newline_idx += 1

        items = \
            items[0:first_trailing_newline_idx] +\
            other.items + items[first_trailing_newline_idx:]

        return TodoList(
            items
            )

    def copy(self):
        return TodoList(self.copy_of_items())

    def deep_copy(self):
        return TodoList(self.deep_copy_of_items())

    def to_file(self, path):
        text = self.as_plain_text(
            with_ids=False,
            indent=True
        ).code('utf-8')

        with open(path, 'w') as f:
            f.write(text)


    def copy_of_items(self):
        return [item.copy() for item in self.items if item]

    def deep_copy_of_items(self):
        return [item.deep_copy() for item in self.items]

    def remove_item(self, item):
        self.items.remove(item)

    def set_parent_list(self, items):
        for item in items:
            item.parent_list = self

    def add_parent(self, parent):
        for item in self.items:
            item.add_parent(parent)

    def indent(self, level=1):
        for item in self.items:
            item.indent(level)

    def set_indent_level(self, level):
        for item in self.items:
            item.set_indent_level(level)

    def remove_tag(self, tag):
        """removes every occurrence of given tag in list"""
        for item in self.items:
            item.remove_tag(tag)

    def tag_with_parents(self):
        """
        add tag `parents` with `/` separated list of parents
        to every item
        """
        for item in self.items():
            item.tag_with_parents()

    def flatten(self):
        """returns as flat list of items"""
        flattened = []
        for item in self.items:
            flattened += item.flatten()
        return flattened

    def prepend(self, items_list):
        self.set_parent_list(items_list)
        self.items = items_list + self.items

    def append(self, items_list):
        self.set_parent_list(items_list)
        self.items += items_list

    def find_project_id_by_title(self, title):
        """
        returns id of first project of given title in list
        returns None when there is no such item
        """
        filtered = self.filter('content = ' + title + ' and type ="project"')
        for item in filtered.items:
            if item.title.content == title:
                return item.title._id
            else:  # check subtasks recursively
                if item.sub_tasks:
                    q = item.sub_tasks.find_project_id_by_title(title)
                    if q:
                        return q
        return None

    def filter(self, predicate, remove=False):
        """
        returns new list that contains only elements that
        meet predicate.

        Also if `remove` is set to True removes those elements
        from self.
        """
        # parse predicate if it's in string
        if isinstance(predicate, unicode) or isinstance(predicate, str):
            predicate = parse_predicate(predicate)

        filtered_items_with_None = [
            item.filter(predicate, remove) for item in self.items
        ]
        filtered_items = [
            item for item in filtered_items_with_None if item
        ]
        new_list = TodoList(filtered_items)
        return new_list

    def as_plain_text(self, with_ids=False, indent=True):
        items_texts_list = [
            item.as_plain_text(with_ids, indent) for item in self.items
        ]
        return "\n".join(items_texts_list)

    def as_countdown(self):
        today = date.today().isoformat()
        only_due = self.filter(
            '((@due and not @done) or (@due >=' + today + ')) and not (@waiting > ' + today + ')'
        )
        items_with_None = [
            item.as_countdown() for item in only_due.items
        ]
        items = [
            item for item in items_with_None if item
        ]
        items.sort()
        return '\n'.join(items)

    def as_markdown(self, emphasise_done=False):
        return "\n".join(
            [item.as_markdown(emphasise_done) for item in self.items]
        )

    def as_html(self):
        items_html = "\n".join([item.as_html() for item in self.items])
        return "<ul>" + items_html + "</ul>"

    def as_full_html(self, css_style=None):
        return """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    {1}
</head>
<body>
<div class="container">
    {0}
</div>
</body>""".format(
    self.as_html(),
    """<link href="{0}" rel="stylesheet" type="text/css" />""".format(
        css_style
    ) if css_style else ''
)
    def pythonista_print(self):
    	for item in self.items:
    		item.pythonista_print()

class ItemTitle(object):
    def __init__(self, line, line_no, indent_level, typ):
        self.line = line
        self.text = extract_text(typ, line)
        self.content = extract_content(typ, line)
        self.type = typ
        # line, text & content at the moment
        # contain some redundant data

        self._id = TodoList.assign_id(self)
        self.line_no = line_no
        self.indent_level = indent_level

        self.prefix = ''
        self.postfix = ''

    def deep_copy(self):
        new = ItemTitle(
            line=self.line,
            line_no=0,
            indent_level=self.indent_level,
            typ=self.type
        )
        new.prefix = self.prefix
        new.postfix = self.postfix
        return new

    def set_indent_level(self, level):
        self.indent_level = level

    def remove_indent(self):
        self.indent_level = 0

    def indent(self, level=1):
        self.indent_level += level

    def tag(self, tag_text, param=None):
        self.line = add_tag_to_text(self.line, tag_text, param)
        self.text = add_tag_to_text(self.text, tag_text, param)

    def remove_tag(self, tag):
        self.text = remove_tag_from_text(self.text, tag)
        self.line = remove_tag_from_text(self.line, tag)
        self.content = remove_tag_from_text(self.content, tag)

    def has_tag(self, tag):
        return bool(re.search("(^| )" + tag + "($| |\()", self.text))

    def has_tags(self, tags):
        return all(self.has_tag(tag) for tag in tags)

    def has_any_tags(self, tags):
        return any(self.has_tag(tag) for tag in tags)

    def get_tag_param(self, tag):
        tag_search = '(^|(?<=\s))' + tag + r'\(([^)]*)\)'
        match = re.search(tag_search, self.text)
        if match:
            return match.group(2)

    def is_done(self):
        return bool(re.search(done_tag, self.line))

    def pythonista_print(self):
    	indent = '\t'*self.indent_level
    	print indent + self.text
    	set_size(12)
    	print indent + '/' + str(self._id)
    	

class Item(object):
    """
    Abstract item on todolist
    """
    def __init__(self, line='', line_no=None, indent_level=None, sub_tasks=None, typ='item'):
        self.title = ItemTitle(line, line_no, indent_level, typ)
        self.parent_item = None  # Project, Task or Note
        self.parent_list = None  # TodoList
        self.type = typ

        self.sub_tasks = sub_tasks
        TodoList.items_by_id[self.title._id] = self

        if self.sub_tasks:
            self.sub_tasks.add_parent(self)

    def __eq__(self, other):
        return self.title == other.title

    def __str__(self):
        return self.as_plain_text()

    def get_content(self):
        return self.title.content

    def copy(self):
        new = self.empty()
        new.title = self.title
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sub_tasks = self.sub_tasks.copy() if self.sub_tasks else None
        new.type = self.type
        return new

    def deep_copy(self):
        new = self.empty()
        new.title = self.title.deep_copy()
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sub_tasks = self.sub_tasks.deep_copy() if self.sub_tasks else None
        new.type = self.type
        return new

    def index(self):
        return self.parent_list.items.index(self)

    def remove_indent(self):
        self.title.remove_indent()

    def indent(self, level=1):
        self.title.indent(level)
        if self.sub_tasks:
            self.sub_tasks.indent(level)

    def tag(self, tag_text, param=None):
        self.title.tag(tag_text, param)

    def tag_with_parents(self):
        self.tag('parents', self.parents_to_str())

    def remove_tag(self, tag):
        self.title.remove_tag(tag)
        if self.sub_tasks:
            self.sub_tasks.remove_tag(tag)

    def has_tag(self, tag):
        return self.title.has_tag(tag)

    def has_tags(self, tags):
        return self.title.has_tags(tags)

    def has_any_tags(self, tags):
        return self.title.has_any_tags(tags)

    def get_tag_param(self, tag):
        return self.title.get_tag_param(tag)

    def parents_to_str(self):
        parents_contents = []
        item = self
        while item.parent_item:
            parents_contents.append(item.parent_item.title.content)
            item = item.parent_item
        return ' / '.join(parents_contents[::-1])

    def add_parent(self, parent):
        self.parent_item = parent

    def remove_self_from_parent(self):
        self.parent_list.remove_item(self)

    def indent_new_subtasks(self, items):
    	try:
    		for item in items.items:
    			item.set_indent_level(self.title.indent_level + 1)
    	except:
    		items.set_indent_level(self.title.indent_level + 1)

    def set_indent_level(self, level):
        self.title.indent_level = level
        if self.sub_tasks:
            self.sub_tasks.set_indent_level(level + 1)

    def prepend_subtasks(self, items):
        self.indent_new_subtasks(items)
        if self.sub_tasks:
            self.sub_tasks = items + self.sub_tasks
        else:
            self.sub_tasks = items

    def append_subtasks(self, items):
        self.indent_new_subtasks(items)
        if self.sub_tasks:
            self.sub_tasks = self.sub_tasks + items
        else:
            self.sub_tasks = items  

    def flatten(self):
        self.tag_with_parents()
        flattened = []
        if self.type in ('note', 'task'):
            flattened.append(self.copy())
        if self.sub_tasks:
            flattened += self.sub_tasks.flatten()
        return flattened

    def is_type(self, typ):
        return self.type == typ

    def is_done(self):
        return self.title.is_done()

    def filter(self, predicate, remove=False):
        """
        Returns new item (with the same title object)
        if item itself or any of subtasks meets predicate.

        Subtasks of item are also filtered.

        If `remove` is set to True removes items that meet
        predicate from subtasks.
        """
        new = self.copy()
        if self.sub_tasks:
            new.sub_tasks = self.sub_tasks.filter(predicate, remove)
        meets_prediacate = predicate.test(self)
        if remove and new.sub_tasks:
            for item in new.sub_tasks.items:
                if predicate.test(item):
                    self.sub_tasks.items.remove(item)
        if meets_prediacate or new.sub_tasks:
            return new

    def as_plain_text(self, with_ids=False, indent=True):
        ptext = (u"{indent}{ident}"
                u"{prefix}"
                u"{text}"
                u"{postfix}"
                u"{sub_tasks}").format(
            ident=(
                (unicode(self.title._id) + ' | ') if with_ids else ''
            ),
            indent=(
                ('\t' * self.title.indent_level) if indent else ''
            ),
            text=self.title.text,
            prefix=self.title.prefix,
            postfix=self.title.postfix,
            sub_tasks=(
                ('\n' + self.sub_tasks.as_plain_text(
                    with_ids, indent
                )
                )
                if self.sub_tasks else ''
            ),
        )

        return ptext

    def as_countdown(self):
        if not ' @due(' in self.title.text:
            if self.sub_tasks:
                return self.sub_tasks.as_countdown()

        time_left = date_to_countdown(
            get_tag_param(self.title.line, 'due')
        )

        if time_left:
            text = u"{time_left} {text}{sub_tasks}".format(
                time_left=time_left,
                text=self.title.text,
                sub_tasks=(
                    ('\n' + self.sub_tasks.as_countdown())
                        if self.sub_tasks else ''
                ),
                )
            return text
        else:
            return ''

    def as_html(self):
        css_class_level = min(
            number_of_css_classes,
            self.title.indent_level
        )

        return '<li><span class="{type_class}{done_class}">{text}</span>{sub_tasks}</li>'.format(
            type_class=self.type + str(css_class_level),
            done_class=(
                ' done' if self.is_done() else ''
            ),
            sub_tasks=(
                ('\n' + self.sub_tasks.as_html())
                    if self.sub_tasks else ''
            ),
            text=enclose_tags(
                escape(self.title.text),
                prefix='<span class="tag">',
                postfix='</span>'),
            )

    def markdown_indent_level(self):
        if self.parent_item:
            if self.parent_item.type == 'project':
                return 0
            return self.parent_item.markdown_indent_level() + 1
        else:
            return 0

    def as_markdown(self, emphasise_done):
        indent = self.markdown_indent()
        text = enclose_tags(self.title.text, '**', '**')
        if self.is_done() and emphasise_done:
            text = '*' + text + '*'
        title = indent + text
        sub_tasks = ''
        if self.sub_tasks:
            sub_tasks = '\n' + self.sub_tasks.as_markdown()
        return title + sub_tasks

    def pythonista_print(self):
    	if self.has_tag('@done'):
    		set_color(cdone)
    	elif self.has_tag('@due'):
    		set_color(cdue)
    	elif self.has_tag('@next'):
    		set_color(cnext)
    	elif self.has_tag('@today'):
    		set_color(ctoday)
    	else:
    		set_color(ctask)
    	self.title.pythonista_print()
    	
    	if self.sub_tasks:
    		self.sub_tasks.pythonista_print()

class Project(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='project'):
        super(Project, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'project'


    def markdown_indent_level(self):
        return 0

    def markdown_indent(self):
        return '\n' + '#' * min(self.title.indent_level + 1, 5) + ' '

    def empty(self):
        return Project()

    def pythonista_print(self):
    	set_size(18+20/(self.title.indent_level+1.))
    	super(Project, self).pythonista_print()


class Task(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='task'):
        super(Task, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.title.prefix = '- '
        self.type = 'task'


    def markdown_indent(self):
        return '\t' * self.markdown_indent_level() + '- '

    def empty(self):
        return Task()

    def pythonista_print(self):
    	set_size(18)
    	super(Task, self).pythonista_print()

class Note(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='note'):
        super(Note, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'note'

    def markdown_indent(self):
        return '\n' + '\t' * self.markdown_indent_level()

    def empty(self):
        return Note()

    def pythonista_print(self):
    		set_size(15)
    		super(Note, self).pythonista_print()

class NewLineItem(object):
    def __init__(self):
        self.title = None

    def __getattr__(self, name):
        """
        most functions of NewLineItem returns None and does
        nothing so they don't have to be implemented
        """
        def f(*args, **kwargs):
            pass
        return f

    def as_plain_text(self, *args):
        return ''

    def flatten(self, *args, **kwargs):
        return []

    def as_markdown(self, *args):
        return '\n'

    def copy(self):
        return NewLineItem()

    def deep_copy(self):
        return NewLineItem()

    def as_html(self):
        return "<br>"

    def pythonista_print(self):
        print ''

# todolist
#################################################
# todolist_parser
"""
# Parser of todo list.

Top-down parser of grammar that is almost LL(1).
Conflict is resolved by prefering production 7 over 5.

## Grammar:

    1. TodoList -> Item TodoList .
    2. Item     -> Task SubTasks
    3.           | Project SubTasks
    4.           | Note SubTasks
    5.           | indent TodoList dedent
    6.           | NewLineItem
    7. SubTasks -> indent TodoList dedent
    8.           | .

"""


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    @staticmethod
    def list_from_file(filepath):
        with open(filepath.strip(), 'r') as f:
            tlist = Parser(Lexer([l.decode('utf-8') for l in f.readlines()])).parse()
            tlist.source = filepath
            return tlist

    def parse(self):
        def todolist():
            """parse list"""
            type_on_top = self.lexer.top().type
            new_item = None

            type_to_constructor = {
                'task': Task,
                'project-title': Project,
                'note': Note,
            }

            # depending on type on top of input
            # construct appropriate object
            if type_on_top == 'newline':
                self.lexer.pop()
                new_item = NewLineItem()
            elif type_on_top in type_to_constructor:
                new_item = parse_item(type_to_constructor[type_on_top])
            elif type_on_top == 'indent':  # begining of sublist
                new_item = parse_sublist()
            elif type_on_top in ('dedent', '$'):
                return TodoList()

            return TodoList([new_item]) + todolist()

        def parse_item(constructor):
            """parse Project, Task or Note with its subtasks"""
            lex = self.lexer.pop()
            sub_tasks = None
            type_on_top = self.lexer.top().type
            if type_on_top == 'indent':
                sub_tasks = parse_sublist()
            return constructor(
                lex.text,
                lex.line_no,
                lex.indent_level,
                sub_tasks,
                )

        def parse_sublist():
            """parse part that begins with indent token"""
            self.lexer.pop()
            sublist = todolist()
            type_on_top = self.lexer.top().type
            if type_on_top == 'dedent':  # don't eat $
                self.lexer.pop()
            return sublist

        return todolist()
# todolist_parser
#################################################
# fileslist
"""
module provides functions to store and retrieve paths of
files with todo lists
"""
import os

dir_path = os.path.expanduser(files_list_path)

full_path = dir_path + files_list_name
# create `selection` file if it doesn't exist
try:
    open(full_path, 'r')
except IOError:
    open(full_path, 'w').close()


def change_list(items, change_f):
    # load items from file
    previous = set()
    with open(full_path, 'r') as f:
        text = f.read()
        if text:
            previous = set(text.split('\t'))

    # change items from file using change_f function
    if isinstance(items, str):
        items = set(items.split('\t'))
    new = change_f(previous, items)

    with open(full_path, 'w') as f:
        f.write('\t'.join(new))


def add(items):
    change_list(items, lambda p, i: p.union(i))


def remove(items):
    change_list(items, lambda p, i: p - set(i))


def clear():
    with open(full_path, 'w') as f:
        f.write('')


def to_list():
    with open(full_path, 'r') as f:
        return f.read().split('\t')
# fileslist
#################################################
# main
"""
Main module, provides functions needes to
create TodoList object from plain text files
and operations that use items unique id like
tagging and removing.
"""

abbreviations = quick_query_abbreviations
conjuction = quick_query_abbreviations_conjuction
import os.path
import subprocess


def from_file(path):
    return Parser.list_from_file(path)


def from_files(paths):
    """
    Constructs todolist from many files,
    content of the file is inserted to project that has
    file name as title

    paths - collection of path or tab separated string
    """
    if isinstance(paths, str):
        paths = paths.split('\t')
    items = []
    for path in paths:
        tlist = from_file(path)
        tlist.indent()
        # set file name as project title
        title = os.path.splitext(os.path.basename(path))[0] + ':'
        p = Project(line=title, sub_tasks=tlist)
        p.source = path  # set source to use in `save` function
        items.append(p)
    return TodoList(items)


def do(item_id):
    TodoList.do(item_id)


def tag(item_id, tag, param=None):
    TodoList.tag(item_id, tag, param)


def remove_task(item_id):
    TodoList.remove(item_id)


def get_content(item_id):
    return TodoList.get_content(item_id)


from urllib import urlencode, quote_plus
import clipboard

def tag_dependand_action(item_id):
    item = TodoList.get_item(item_id)
    content = item.get_content()
    
    if item.has_any_tags(['@search', '@research']):
        action.x_callend('bang-on://?' + urlencode({'q': content}))
    elif item.has_tag('@web'):
        action.x_callend(item.get_tag_param('@web'))
    elif item.has_tag('@mail'):
    	clipboard.set(content)
    	s = 'mailto:{0}'.format(item.get_tag_param('@osoba').split('<')[1][0:-1])
    	action.x_callend(s)

finished = False

class action():
    @staticmethod
    def x_call(s):
    	webbrowser.open(s)
 
    @staticmethod
    def x_callend(s):
    	global finished
    	action.x_call(s)
    	finished=True 

    @staticmethod
    def open(s):
    	webbrowser.open(s)

def add_new_subtask(item_id, new_item):
    """
    new_item should be item of type Task, Project, Note or
    string, in that case it's assumed that it's task
    """
    if isinstance(new_item, unicode) or isinstance(new_item, str):
        new_item = TodoList([Task('- ' + new_item)])
    TodoList.items_by_id[item_id].append_subtasks(new_item)


def expand_shortcuts(query):
    if query == '':
        return ''
    if query[0] == ' ':  # no abbreviations
        return query.strip()
    else:
        expanded_query = []
        # expand abbreviations till first space
        first_space_idx = query.find(' ')
        if first_space_idx == -1:
            first_space_idx = len(query)

        for i in range(0, first_space_idx):
            expanded_query.append(abbreviations[query[i]])
        expanded_query.append(query[first_space_idx + 1:])
        return conjuction.join(expanded_query)


def archive(tlist, archive_tlist=None):
    """
    moves @done items to first project of title Archive
    assumes that it exsits
    if `archive_tlist` is not specified puts archived items
    to itself
    """
    done = tlist.filter('@done and project != Archive', remove=True)
    done_list = done.deep_copy().flatten()
    if not archive_tlist:
        archive_tlist = tlist
    arch_id = archive_tlist.find_project_id_by_title('Archive')
    TodoList.items_by_id[arch_id].prepend_subtasks(TodoList(done_list))


def move(fro, to):
	to_item = TodoList.items_by_id[to]
	for f in fro:
		item = TodoList.items_by_id[f]
		item.remove_self_from_parent()
		to_item.append_subtasks(TodoList([item]))
    

def save(tlist):
    """
    Use to save changes to individual files of todolist constructed
    by `from_files` function.

    At the moment it's inefficient - function rewrites every file,
    even if todo list from it wasn't modified. If I notice that
    it has influence on workflow I'll improve this.
    """
    for item in tlist.items:
        if hasattr(item, 'source'):
            with open(item.source.strip(), 'w') as f:
                item.sub_tasks.indent(-1)
                f.write(item.sub_tasks.as_plain_text().encode('utf-8'))

t = None
fq = ''

import clipboard

def dispatch(inp):
	i = inp[0]
	r = inp[1:]
	if i == 'q':
		t.filter(expand_shortcuts(r)).pythonista_print()
	elif  i == 'd':
		do(int(r))
		save(t)
		t.filter(fq).pythonista_print()
	elif i == 'c':
		clipboard.set(get_content(int(r)))
	elif i == 'a':
		tag_dependand_action(int(r))
	elif i == 'm':
		fro, to = r.split('>')
		fro = [f.strip() for f in fro.split(' ')]
		fro = [int(f) for f in fro if f]
		to = int(to.strip())
		move(fro, to)
		save(t)
		t.filter(fq).pythonista_print()
	#elif i == '+':
	#	ide, tas = r.partition(' ')[::2]
	#	print ide, tas
	#	ide = int(ide.strip())
	#	add_new_subtask(ide, tas)
	#	save(t)
	#	t.filter(fq).pythonista_print()
	else:
		print inp + '?'

def q(query=''):
	global t
	global fq
	fq = query
	t = from_files(to_list())
	t.filter(query).pythonista_print()
	inp = raw_input()
	while inp != '':
		dispatch(inp)
		if not finished:
			inp = raw_input()
		else: 
			break
	set_color((0.,0.,0.))
	console.set_font()
	

