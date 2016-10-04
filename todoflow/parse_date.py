from collections import namedtuple
from datetime import datetime
import parsedatetime


Token = namedtuple('Token', ['type', 'value'])


punctuations = (
    '+', '-', ':'
)
numbers = (
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
)
white_space = (
    ' ', '\t', '\n'
)
word_breaks = punctuations + numbers + white_space
words = {
    'ampm': (
        'am', 'pm'
    ),
    'date': (
        'today', 'yesterday', 'tomorrow', 'now'
    ),
    'time': (
        'now'
    ),
    'month': (
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
        'aug', 'sep', 'oct', 'nov', 'dec',
    ),
    'day': (
        'sunday', 'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday',
        'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat',
    ),
    'modifier': (
        'next', 'last'
    ),
    'duration': (
        'minute', 'minutes',
        'h', 'hour', 'hours',
        'd', 'day', 'days',
        'w', 'week', 'weeks',
        'm', 'month', 'months'
        'y', 'year', 'years',
    ),
}


def iterate_parts(l, size):
    index = 0
    while index + size <= len(l):
        yield l[index:index + size]
        index += 1


def matches(l, predicates):
    return all(
        p(i) for i, p in zip(l, predicates)
    )


class Lexer:
    def tokenize(self, text):
        self.chars = list(text.lower())
        self.tokens = []
        word = ''
        while self.chars:
            c = self.pick()
            if c in white_space:
                self.pop()
                continue
            elif c in numbers:
                self.read_number()
            elif c in punctuations:
                self.read_punctuation()
            else:
                self.read_word()
        return self.tokens

    def pick(self):
        if not self.chars:
            return None
        return self.chars[0]

    def pop(self):
        return self.chars.pop(0)

    def read_number(self):
        number = ''
        while self.pick() and self.pick() in numbers:
            number += self.pop()
        self.add('number', int(number))

    def read_punctuation(self):
        self.add('punctuation', self.pop())

    def read_word(self):
        word = ''
        while self.pick() and self.pick() not in word_breaks:
            word += self.pop()
        self.add('word', word)

    def add(self, type, value):
        if type == 'word':
            for k, values in words.items():
                if value in values:
                    self.add(k, value)
                    break
        else:
            self.tokens.append(Token(type, value))


def parse_date(text=''):
    cal = parsedatetime.Calendar()
    time_sctruct, _ = cal.parse(text)
    return datetime(*time_sctruct[:6])
