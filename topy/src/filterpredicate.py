import re

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


class Token(object):
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
        elif text in Token.operators:
            self.type = 'op'
        elif text == '+d':
            self.type = 'plusD'
        elif text in Token.log_ops:
            self.type = text
        elif text in Token.keywords:
            self.type = 'arg'
        elif text[0] == Token.tag_prefix:
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


class Lexer(object):
    def __init__(self, input_text):
        self.tokens = Lexer.tokenize(input_text)

    @staticmethod
    def tokenize(input_text):
        """converts input text to list of tokens"""
        tokens = []

        def add_token(text=None):
            if text != '' and text != ' ':
                tokens.append(Token(text))

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


class Parser(object):
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
    return Parser(Lexer(text)).parse()
