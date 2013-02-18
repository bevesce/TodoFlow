import re


class Token(object):
    tag_pattern = re.compile(r'[^\(\s]*(|\([^)]*\))')

    @staticmethod
    def is_task(line, indent_level):
        return line.strip()[0:2] == '- '

    @staticmethod
    def is_project(line):
        splitted = line.split(':')
        if len(splitted) < 2:
            return False
        if line[-1] == ' ':
            return False

        after_colon = splitted[-1].split('@')
        only_tags_after_colon = all([
           Token.tag_pattern.match(tag) for tag in after_colon
            ])
        return only_tags_after_colon

    def __init__(self, line=None, indent_level=0, line_no=0):
        if not line is None:
            self.indent_level = indent_level
            self.line_no = line_no

            if Token.is_task(line, indent_level):
                self.text = line
                self.type = 'task'
            elif Token.is_project(line):
                self.text = line
                self.type = 'project-title'
            elif line == '':
                self.text = ''
                self.type = 'newline'
            else:
                self.text = line
                self.type = 'note'
        else:
            self.type = '$'
            self.text = '$'

    def __repr__(self):
        return self.type + ' : ' + self.text


class Dedent(Token):
    def __init__(self):
        self.type = 'dedent'
        self.text = 'dedent'


class Indent(Token):
    def __init__(self):
        self.type = 'indent'
        self.text = 'indent'


class NewLine(Token):
    def __init__(self):
        self.type = 'newline'
        self.text = '\n'


class Lexer(object):
    def __init__(self, lines):
        self.tokens = Lexer.tokenize(lines)

    @staticmethod
    def from_file(filepath):
        with open(filepath, 'r') as f:
            return Lexer(f.readlines())

    @staticmethod
    def indent_level(text):
        level = 0
        while level < len(text) and text[level] == '\t':
            level += 1
        return level

    @staticmethod
    def tokenize(lines):
        indent_levels = [0]
        tokens = []
        for line_idx, line in enumerate(lines):
            if line == '\n':
                tokens.append(NewLine())
                continue

            current_level = Lexer.indent_level(line)
            if current_level > indent_levels[-1]:
                indent_levels.append(current_level)
                tokens.append(Indent())
            elif current_level < indent_levels[-1]:
                while current_level < indent_levels[-1]:
                    indent_levels.pop()
                    tokens.append(Dedent())
            tokens.append(Token(line, current_level, line_idx))
        return [Token()] + tokens[::-1]

    def top(self):
        return self.tokens[-1]

    def pop(self):
        return self.tokens.pop()

    def consume(self, typ, or_eof=False):
        if self.tokens.pop().type != typ:
            raise ParseError


class ParseError(Exception):
    pass
