import re

def create_tag_pattern(tag):
    tag = fix_tag(tag)
    return re.compile(r'(?<=\s)' + tag + r'(\([^)]*\)|)(?=(\s|$))')    

def remove_tag(txt, tag):
    p = create_tag_pattern(tag)
    return p.sub('', txt).rstrip()

def add_tag(txt, tag, param=None, index=None):
    tag = fix_tag(tag)
    if param:
        tag += '(' + str(param) + ')'
    if not index:
        txt = append_space(txt)
        return txt + tag
    else:
        first_part = append_space(txt[:index])
        second_part = prepend_space(txt[index:])
        return first_part + tag + second_part

def get_tag_param(txt, tag):
    p = create_tag_pattern(tag)
    match = p.search(txt)
    if not match:
        return None
    return match.group(1)[1:-1]

def has_tag(txt, tag):
    p = create_tag_pattern(tag)
    return bool(p.search(txt))

def append_space(txt):
    if not txt.endswith(' '):
        txt += ' '
    return txt

def prepend_space(txt):
    if not txt.startswith(' '):
        return ' ' + txt
    return txt

def remove_tags(txt):
    for rx in [
        r'\s@[^(\s]*\([^)]*?\)',
        r'\s@[^\[\s]*\[[^)]*?\]',
        r'\s@[^\{\s]*\{[^)]*?\}',
        r'\s@\S*',
    ]:
        p = re.compile(rx)
        txt = p.sub(' ', txt)
    while '  ' in txt:
        txt = txt.replace('  ', ' ')
    return txt.rstrip()


def fix_tag(txt):
    if not txt.startswith('@'):
        return '@' + txt
    else:
        return txt


# ( everything but `)` ) or lookahead for \s or end of line
tag_param_regexp = r'(\(([^)]*)\)|(?=(\s|$)))'
# prepend word (sequence without \s and `(`)
tag_regexp_without_at = r'[^\(\s]+' + tag_param_regexp
tag_pattern_without_at = re.compile(tag_regexp_without_at + r'\Z')
# prepend '@'
tag_pattern = re.compile('(?<!^)(@' + tag_regexp_without_at + ')')

def enclose_tags(text, prefix, postfix):
    """
    puts `prefix` before and `postfix` after
    every tag in text
    """
    def f(t):
        return prefix + t.group(1) + postfix
    return re.sub(tag_pattern, f, text)


def task_cmp(tag):
    def f(task1, task2):
        has_tag1 = has_tag(task1, tag)
        has_tag2 = has_tag(task2, tag)
        if not has_tag1 and not has_tag2:
            return 0
        elif not has_tag1 and has_tag2:
            return -1
        elif has_tag1 and not has_tag2:
            return 1
        else:
            p1 = get_tag_param(task1, tag)
            p2 = get_tag_param(task2, tag)
            return cmp(p1, p2)
    return f


def sort_by_tag(lines, tag):
    return sorted(lines, cmp=task_cmp(tag))