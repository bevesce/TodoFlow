import re

def create_tag_pattern(tag):
    if not tag.startswith('@'):
        tag = '@' + tag
    p = re.compile(
        '\s' + tag + '(\s|$|'  '\([^)]*\)'  '|' '\[[^\]]*\]' '|' '\{[^}]}' ')'
    )
    return p, 1


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