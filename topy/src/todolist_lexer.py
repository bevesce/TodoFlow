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
import re


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
            if line == '\n':
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
