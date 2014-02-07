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