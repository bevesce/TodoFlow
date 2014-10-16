from __future__ import absolute_import

from .textutils import calculate_indent_level


class Token(object):
    token_ids = {
        'text': '*',
        'newline': 'n',
        'indent': '>',
        'dedent': '<',
        'end': '$',
    }

    def __getattr__(self, attr_name):
        try:
            return self.token_ids[attr_name.split('_')[-1]] == self.tok()
        except KeyError:
            raise AttributeError


class NewlineToken(Token):
    def tok(self):
        return self.token_ids['newline']


class IndentToken(Token):
    def tok(self):
        return self.token_ids['indent']


class DedentToken(Token):
    def tok(self):
        return self.token_ids['dedent']


class TextToken(Token):
    def __init__(self, text):
        self.text = text

    def tok(self):
        return self.token_ids['text']


class EndToken(Token):
    def tok(self):
        return self.token_ids['end']


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.lines = text.splitlines()
        if text.endswith('\n'):
            self.lines.append('')
        self._tokenize()

    def _tokenize(self):
        self.tokens = []
        self.indent_levels = [0]
        for line_num, line in enumerate(self.lines):
            if line:
                self._handle_indentation(line)
                self.tokens.append(TextToken(line))
            else:
                self.tokens.append(NewlineToken())
        self.tokens.append(EndToken())

    def _handle_indentation(self, line):
        indent_levels = self.indent_levels
        current_level = calculate_indent_level(line)
        if current_level > indent_levels[-1]:
            indent_levels.append(current_level)
            self.tokens.append(IndentToken())
        elif current_level < indent_levels[-1]:
            while current_level < indent_levels[-1]:
                indent_levels.pop()
                self.tokens.append(DedentToken())
