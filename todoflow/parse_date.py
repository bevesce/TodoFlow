from collections import namedtuple
from datetime import datetime, timedelta
import calendar
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



months = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,

    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}
days = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6,
    'mon': 0,
    'tue': 1,
    'wed': 2,
    'thu': 3,
    'fri': 4,
    'sat': 5,
    'sun': 6,
}


words = {
    'ampm': ('am', 'pm'),
    'date': ('today', 'yesterday', 'tomorrow', 'now'),
    'month': list(months.keys()),
    'day': list(days.keys()),
    'modifier': ('next', 'last'),
    'duration': (
        'minute', 'minutes', 'min',
        'h', 'hour', 'hours',
        'd', 'day', 'days',
        'w', 'week', 'weeks',
        'm', 'month', 'months'
        'y', 'year', 'years',
    ),
}




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


empty_token = Token(None, None)


class Parser:
    def parse(self, text, now=None):
        self.tokens = Lexer().tokenize(text)
        self.modifications = []
        self.now = now or datetime.now()
        self.today = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.date = self.now
        while self.tokens:
            t = self.pick()
            if t.type == 'ampm':
                self.pop()
            elif t.type == 'date':
                self.parse_date()
            elif t.type == 'month':
                self.parse_month()
            elif t.type == 'day':
                self.parse_day()
            elif t.type == 'modifier':
                self.parse_modifier()
            elif t.type == 'duration':
                self.parse_duration()
            elif t.type == 'punctuation':
                self.parse_punctuation()
            elif t.type == 'number':
                self.parse_number()
            else:
                self.pop()
        for modification in self.modifications:
            self.date = modification(self.date)
        return self.date

    def pick(self):
        if not self.tokens:
            return empty_token
        return self.tokens[0]

    def pickpick(self):
        return self.tokens[1]

    def pop(self):
        return self.tokens.pop(0)

    def is_eof(self):
        return not self.tokens

    def parse_date(self):
        date = self.pop().value
        today = self.today
        if date == 'today':
            self.date = today
        if date == 'now':
            self.date = self.now
        if date == 'yesterday':
            self.date = today - timedelta(days=1)
        if date == 'tomorrow':
            self.date = today + timedelta(days=1)


    def parse_month(self):
        month = self.pop().value
        self.modifications.append(
            lambda d: d.replace(month=months[month], day=1)
        )
        next = self.pick()
        if next.type == 'number' and next.value <= 31:
            self.pop()
            self.modifications.append(
                lambda d: d.replace(day=next.value)
            )

    def parse_day(self):
        day = self.pop().value
        self.modifications.append(
            lambda d: self.find_weekday_in_week_of(d, day)
        )

    def parse_modifier(self):
        modifier = self.pop().value
        next = self.pick()
        sign = 1 if modifier == 'next' else -1
        if next.type == 'day':
            day = self.pop().value
            self.modifications.append(
                lambda d: self.find_weekday_in_week_of(d, day) + timedelta(days=sign * 7)
            )
        elif next.type == 'month':
            month = self.pop().value
            self.modifications.append(
                lambda d: d.replace(year=d.year + sign, month=months[month], day=1)
            )
        elif next.type == 'duration':
            duration = self.pop().value
            if duration in ('year', 'years', 'y'):
                self.modifications.append(
                    lambda d: d.replace(year=d.year + sign, month=1, day=1, hour=0, second=0, microsecond=0)
                )
            elif duration in ('month', 'months', 'm'):
                self.modifications.append(
                    lambda d: self.add_months(d, sign).replace(day=1, hour=0, second=0, microsecond=0)
                )
            elif duration in ('week', 'weeks', 'w'):
                self.modifications.append(
                    lambda d: self.find_weekday_in_week_of(d, 'mon') + timedelta(days=7 * sign)
                )
            elif duration in ('day', 'days', 'd'):
                self.modifications.append(
                    lambda d: (d + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                )
            elif duration in ('hour', 'hours', 'h'):
                self.modifications.append(
                    lambda d: (d + timedelta(hours=sign)).replace(minute=0, second=0, microsecond=0)
                )
            elif duration in ('minute', 'minutes', 'min'):
                self.modifications.append(
                    lambda d: (d + timedelta(minutes=sign)).replace(second=0, microsecond=0)
                )

    def parse_duration(self):
        self.pop()

    def parse_punctuation(self):
        punctuation = self.pop().value
        if punctuation == ':':
            return
        next = self.pick()
        sign = -1 if punctuation == '-' else 1
        if next.type == 'number':
            number = self.pop().value
            next = self.pick()
            if next.type == 'duration':
                duration = self.pop().value
                self.modifications.append(
                    lambda d: self.add_to_date(d, sign * number, duration)
                )
            else:
                self.modifications.append(
                    lambda d: self.add_to_date(d, sign * number, 'days')
                )

    def parse_number(self):
        first_number = self.pop().value
        next = self.pick()
        if next.type == 'punctuation' and next.value == ':':
            self.pop()
            next = self.pick()
            if next.type == 'number':
                minute = self.pop().value
                self.modifications.append(
                    lambda d: d.replace(hour=first_number, minute=minute)
                )
        elif next.type == 'ampm':
            self.pop()
            if next.value == 'pm':
                first_number += 12
            self.modifications.append(
                lambda d: d.replace(hour=first_number)
            )
        elif next.type == 'punctuation' and next.value == '-':
            second_number = None
            third_number = None
            nextnext = self.pickpick()
            if nextnext.type == 'number':
                self.pop()
                second_number = self.pop().value
            next = self.pick()
            if next.type == 'punctuation' and next.value == '-':
                nextnext = self.pickpick()
                if nextnext.type == 'number':
                    self.pop()
                    third_number = self.pop().value
            self.date = datetime(first_number, second_number or 1, third_number or 1)
        elif next.type == 'duration':
            duration = self.pop().value
            self.modifications.append(
                lambda d: self.add_to_date(d, first_number, duration)
            )
        else:
            self.date = datetime(first_number, 1, 1)

    def find_weekday_in_week_of(self, date, weekday):
        day_number = days[weekday]
        return date + timedelta(days=-date.weekday() + day_number)

    def add_to_date(self, date, number, duration):
        if duration in ('minute', 'minutes', 'min'):
            return date + timedelta(minutes=number)
        if duration in ('hour', 'hours', 'h'):
            return date + timedelta(hours=number)
        if duration in ('day', 'days', 'd'):
            return date + timedelta(days=number)
        if duration in ('week', 'weeks', 'w'):
            return date + timedelta(days=number * 7)
        if duration in ('month', 'months', 'm'):
            return self.add_months(date, number)
        if duration in ('year', 'years', 'y'):
            return date.replace(year=date.year + number)

    def add_months(self, date, number):
        # http://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
        month = date.month - 1 + number
        year = int(date.year + month / 12 )
        month = month % 12 + 1
        day = min(date.day,calendar.monthrange(year,month)[1])
        return datetime(
            year, month, day, date.hour, date.minute, date.second, date.microsecond
        )


def parse_date(text='', now=None):
    return Parser().parse(text, now)
