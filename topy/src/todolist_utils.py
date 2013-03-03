"""
Module provides functions used by objects in todolist module,
mostly operations on text.
"""

import colors
import re
from datetime import date

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


def get_actual_colors(def_colors, colored, is_done, is_overdue=False):
    """
    What color we want to use in text depends
    on three conditions `colored`, `is_done`, `is_overdue`.

    Function gets one dict of colors `def_colors` and returns
    new dict that have changes colors accorgind to those
    conditions.
    """
    res = {}
    for k in def_colors:
        if not colored:
            res[k] = ''
        elif is_done:
            res[k] = colors.gray
        else:
            res[k] = def_colors[k]
    res['countdown_text'] = colors.defc

    if is_done:
        res['countdown_text'] = colors.gray
        res['tag_color'] = colors.gray
    elif is_overdue:
        res['countdown_text'] = colors.red
        res['tag_color'] = colors.red
    if not colored:
        res['countdown_text'] = ''
        res['tag_color'] = ''
    return res


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
        print e
        return '?' * number_of_digits
