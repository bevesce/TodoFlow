from collections import namedtuple

Token = namedtuple('Token', ['type', 'value'])


class LexerError(Exception):
    pass


class QueryLexer:
    def run(self, text):
        self.chars = list(text)
        self.tokens = []
        while not self.is_eof():
            c = self.pick()
            if self.is_attribute_start(c):
                self.read_attribute()
            elif self.is_wild_card(c):
                self.read_wild_card()
            elif self.is_punctuation(c):
                self.read_punctuationn()
            elif self.is_axis_selector_start(c):
                self.read_axis_selector()
            elif self.is_quote(c):
                self.read_search_term()
            elif self.is_operator_start(c):
                self.read_operator()
            elif self.is_slice_or_modifier_start(c):
                self.read_slice_or_modifier()
            else:
                self.read_search_term_word_operator_or_shortcut()
        return self.tokens

    def pick(self):
        return self.chars[0]

    def pop(self):
        return self.chars.pop(0)

    def pop_word(self, word):
        self.chars = self.chars[len(word):]
        return word

    def push(self, token):
        self.tokens.append(token)

    def startswith(self, text):
        return ''.join(self.chars).startswith(text)

    def is_eof(self):
        return not self.chars

    def is_word_break(self, c):
        if self.is_eof():
            return True
        return c in '/@=!<>[]()"'

    def is_quote(self, c):
        return c == '"'

    def is_slice_or_modifier_start(self, c):
        return c == '['

    def is_slice_or_modifier_end(self, c):
        return c == ']'

    def is_attribute_start(self, c):
        return c == '@'

    def is_keyword(self, text):
        return text in (
            'project',
            'task',
            'note',
        )

    def is_operator(self, text):
        return text in (
            '=', '!=', '<', '>', '<=', '>=',
        )

    def is_wild_card(self, c):
        return c == '*'

    def is_operator_start(self, c):
        return c in '=<!>/'

    def is_operator_second_part(self, operator, c):
        if operator in '!<>':
            return c == '='

    def is_axis_selector_start(self, c):
        return c == '/'

    def is_word_operator(self, text):
        return text in (
            'contains',
            'beginswith',
            'endswith',
            'matches',
            'union',
            'intersect',
            'except',
            'and',
            'or',
            'not',
        )

    def is_relation_modifier(self, c):
        return c in 'isnd'

    def is_punctuation(self, c):
        return c in '()'

    def is_number(self, c):
        try:
            int(c)
            return True
        except ValueError:
            return False

    def is_slice(self, text):
        if ':' not in text:
            return self.is_number(text)
        try:
            start, end = text.split(':')
        except ValueError:
            return False
        start_ok = start == '' or self.is_number(start)
        end_ok = end == '' or self.is_number(end)
        return start_ok and end_ok

    def is_shortcut(self, text):
        return text in (
            'project', 'note', 'task'
        )


    def read_attribute(self):
        self.pop()
        value = self.read_while_not(self.is_word_break)
        self.add('attribute', value)

    def read_axis_selector(self):
        axis_selectors = (
            '/ancestor-or-self::',
            '/ancestor::',
            '/descendant-or-self::',
            '/descendant::',
            '/following-sibling::',
            '/following::',
            '/preceding-sibling::',
            '/preceding::',
            '/child::',
            '/parent::',
            '///',
            '//',
            '/',
        )
        for axis_selector in axis_selectors:
            if self.startswith(axis_selector):
                self.pop_word(axis_selector)
                self.add('axis', axis_selector)

    def read_punctuationn(self):
        self.add('punctuation', self.pop())

    def read_operator(self):
        first_char = self.pop()
        if self.is_eof():
            self.add('operator', first_char)
            return
        second_char = self.pick()
        if self.is_operator_second_part(first_char, second_char):
            self.add('operator', first_char + self.pop())
        else:
            self.add('operator', first_char)

    def read_slice_or_modifier(self):
        self.pop()
        value = self.read_while_not(self.is_slice_or_modifier_end)
        self.pop()
        is_slice = self.is_slice(value)
        is_modifier = self.is_relation_modifier(value)
        if not (is_slice or is_modifier):
            raise LexerError('bad relation modifier', value)
        type = 'slice' if is_slice else 'relation modifier'
        self.add(type, value)

    def read_wild_card(self):
        self.add('wild card', self.pop())

    def read_search_term_word_operator_or_shortcut(self):
        word = self.read_while_not(self.is_word_break)
        if self.is_word_operator(word):
            self.add('operator', word)
        elif self.is_shortcut(word):
            self.add('shortcut', word)
        else:
            self.add('search term', word)

    def read_search_term(self):
        self.pop()
        search_term = self.read_while_not(self.is_quote)
        self.pop()
        self.add('search term', search_term)

    def read_while_not(self, f):
        word = ''
        if self.is_eof():
            return word
        c = self.pick()
        while not f(c):
            word += self.pop()
            if self.is_eof():
                return word.strip()
            c = self.pick()
        return word.strip()

    def add(self, type, value):
        self.tokens.append(Token(type, value))
