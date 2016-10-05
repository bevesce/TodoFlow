from collections import namedtuple
from datetime import datetime, timedelta
import calendar
import parsedatetime


def parse_date(text='', now=None):
    return Parser(now).parse(text)


Token = namedtuple('Token', ['type', 'value'])


punctuations = ('+', '-', ':')
numbers = tuple(str(i) for i in range(0, 10))
white_space = (' ', '\t', '\n')
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
}
weekdays = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6,
}
synonyms = {
    'mon': 'monday',
    'tue': 'tuesday',
    'wed': 'wednesday',
    'thu': 'thursday',
    'fri': 'friday',
    'sat': 'saturday',
    'sun': 'sunday',
    'jan': 'january' ,
    'feb': 'february',
    'mar': 'march',
    'apr': 'april',
    'may': 'may',
    'jun': 'june',
    'jul': 'july',
    'aug': 'august',
    'sep': 'september',
    'oct': 'october',
    'nov': 'november',
    'dec': 'december',
    'minutes': 'minute',
    'min': 'minute',
    'hours': 'hour',
    'h': 'hour',
    'days': 'day',
    'd': 'day',
    'weeks': 'week',
    'w': 'week',
    'months': 'month',
    'm': 'month',
    'years': 'year',
    'y': 'year',
}
words = {
    'ampm': ('am', 'pm'),
    'date': ('today', 'yesterday', 'tomorrow', 'now'),
    'month': list(months.keys()),
    'weekday': list(weekdays.keys()),
    'modifier': ('next', 'last'),
    'duration': ('minute', 'hour', 'day', 'week', 'month', 'year'),
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
        value = synonyms.get(value, value)
        if type == 'word':
            for k, values in words.items():
                if value in values:
                    self.add(k, value)
                    break
        else:
            self.tokens.append(Token(type, value))


empty_token = Token(None, None)


class Parser:
    def __init__(self, now=None):
        self.now = now or datetime.now()
        self.today = self.now.replace(hour=0, minute=0, second=0, microsecond=0)

    def parse(self, text, now=None):
        self.tokens = Lexer().tokenize(text)
        self.modifications = []
        self.date = self.now
        while self.tokens:
            t = self.pick()
            if t.type == 'ampm':
                self.pop()
            elif t.type == 'date':
                self.parse_date()
            elif t.type == 'month':
                self.parse_month()
            elif t.type == 'weekday':
                self.parse_weekday()
            elif t.type == 'modifier':
                self.parse_modifier()
            elif t.type == 'duration':
                self.pop()
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
        try:
            return self.tokens[1]
        except IndexError:
            return empty_token

    def pop(self):
        return self.tokens.pop(0)

    def is_eof(self):
        return not self.tokens

    def add_modification(self, modification):
        self.modifications.append(modification)

    def parse_date(self):
        date = self.pop().value
        if date == 'now':
            self.date = self.now
        elif date == 'today':
            self.date = self.today
        elif date == 'yesterday':
            self.date = self.today - timedelta(days=1)
        elif date == 'tomorrow':
            self.date = self.today + timedelta(days=1)

    def parse_month(self):
        month = self.pop().value
        self.add_modification(
            lambda d: d.replace(month=months[month], day=1)
        )
        self.maybe_parse_day()

    def maybe_parse_day(self):
        next = self.pick()
        if next.type != 'number' or next.value > 31:
            return False
        day = self.pop().value
        self.add_modification(
            lambda d: d.replace(day=day)
        )
        return True

    def parse_weekday(self):
        day = self.pop().value
        self.add_modification(
            lambda d: find_weekday_in_week_of_date(day, d)
        )

    def parse_modifier(self):
        modifier = self.pop().value
        next = self.pick()
        sign = 1 if modifier == 'next' else -1

        if self.maybe_parse_weekday_after_modifier(sign):
            return
        elif self.maybe_parse_month_after_modifier(sign):
            return
        elif self.maybe_parse_duration_after_modifier(sign):
            return

    def maybe_parse_weekday_after_modifier(self, sign):
        if self.pick().type != 'weekday':
            return False
        day = self.pop().value
        self.add_modification(
            lambda d: find_weekday_in_week_of_date(day, d) + timedelta(days=sign * 7)
        )
        return True

    def maybe_parse_month_after_modifier(self, sign):
        if self.pick().type != 'month':
            return False
        month = self.pop().value
        self.add_modification(
            lambda d: d.replace(year=d.year + sign, month=months[month], day=1)
        )
        return True

    def maybe_parse_duration_after_modifier(self, sign):
        if self.pick().type != 'duration':
            return False
        duration = self.pop().value
        if duration == 'year':
            self.add_modification(
                lambda d: d.replace(year=d.year + sign, month=1, day=1, hour=0, second=0, microsecond=0)
            )
        elif duration == 'month':
            self.add_modification(
                lambda d: add_months(d, sign).replace(day=1, hour=0, second=0, microsecond=0)
            )
        elif duration == 'week':
            self.add_modification(
                lambda d: find_weekday_in_week_of_date('monday', d) + timedelta(days=7 * sign)
            )
        elif duration == 'day':
            self.add_modification(
                lambda d: (d + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif duration == 'hour':
            self.add_modification(
                lambda d: (d + timedelta(hours=sign)).replace(minute=0, second=0, microsecond=0)
            )
        elif duration == 'minute':
            self.add_modification(
                lambda d: (d + timedelta(minutes=sign)).replace(second=0, microsecond=0)
            )

    def parse_punctuation(self):
        punctuation = self.pop().value
        if punctuation == ':':
            return
        next = self.pick()
        sign = -1 if punctuation == '-' else 1
        self.maybe_parse_number_after_minus_or_plus(sign)

    def maybe_parse_number_after_minus_or_plus(self, sign):
        if self.pick().type != 'number':
            return False
        number = self.pop().value
        if self.maybe_parse_duration_after_minus_plus_number(sign, number):
            return
        else:
            self.add_modification(
                lambda d: add_to_date(d, sign * number, 'days')
            )
        return True

    def maybe_parse_duration_after_minus_plus_number(self, sign, number):
        if self.pick().type != 'duration':
            return False
        duration = self.pop().value
        self.add_modification(
            lambda d: add_to_date(d, sign * number, duration)
        )
        return True

    def parse_number(self):
        first_number = self.pop().value
        if self.maybe_parse_24_time(first_number):
            return
        elif self.maybe_parse_ampm_after_number(first_number):
            return
        elif self.maybe_parse_dash_after_number(first_number):
            return
        elif self.maybe_parse_duration_after_number(first_number):
            return
        else:
            self.date = datetime(first_number, 1, 1)

    def maybe_parse_24_time(self, hour):
        t = self.pick()
        if t.type != 'punctuation' or t.value != ':':
            return False
        self.pop()
        self.maybe_parse_minute_after_hour(hour)
        return True

    def maybe_parse_minute_after_hour(self):
        if self.pick().type != 'number':
            return False
        minute = self.pop().value
        self.add_modification(
            lambda d: d.replace(hour=number, minute=minute)
        )
        return True

    def maybe_parse_ampm_after_number(self, number):
        if self.pick().type != 'ampm':
            return False
        am_or_pm = self.pop().value
        if am_or_pm.value == 'pm':
            number += 12
        self.add_modification(
            lambda d: d.replace(hour=number)
        )
        return True

    def maybe_parse_dash_after_number(self, year):
        if not self.maybe_parse_dash():
            return False
        elif self.maybe_parse_month_after_year(year):
            return True
        self.date = datetime(year, 1, 1)
        return True

    def maybe_parse_month_after_year(self, year):
        if self.pick().type != 'number':
            return False
        month = self.pop().value
        if self.maybe_parse_day_after_month_year(year, month):
            return True
        else:
            self.date = datetime(year, month, 1)
            return True

    def maybe_parse_day_after_month_year(self, year, month):
        if not self.maybe_parse_dash():
            return False
        day = self.pop().value
        self.date = datetime(year, month, day)
        return True

    def maybe_parse_dash(self):
        t = self.pick()
        if t.type == 'punctuation' or t.value == '=':
            self.pop()
            return True
        return False

    def maybe_parse_duration_after_number(self, number):
        if self.pick().type != 'duration':
            return False
        duration = self.pop().value
        self.add_modification(
            lambda d: add_to_date(d, number, duration)
        )
        return True


def find_weekday_in_week_of_date(weekday, date):
    day_number = weekdays[weekday]
    return date + timedelta(days=-date.weekday() + day_number)


def add_to_date(date, number, duration):
    if duration == 'minute':
        return date + timedelta(minutes=number)
    if duration == 'hour':
        return date + timedelta(hours=number)
    if duration == 'day':
        return date + timedelta(days=number)
    if duration == 'week':
        return date + timedelta(days=number * 7)
    if duration == 'month':
        return add_months(date, number)
    if duration == 'year':
        return date.replace(year=date.year + number)


def add_months(date, number):
    # http://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
    month = date.month - 1 + number
    year = int(date.year + month / 12)
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime(
        year, month, day, date.hour, date.minute, date.second, date.microsecond
    )
