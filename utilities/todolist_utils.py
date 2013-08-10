"""
Module provides functions used by objects in todolist module,
mostly operations on text.
"""

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


def remove_tags(line):
    return tag_pattern.sub('', line)


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


def remove_tag_from_text(text, tag):
    # TODO: lefts two spaces, maybe fix someday
    tag_pattern = custom_tag_regexp(tag)
    return re.sub(tag_pattern, '', text)
