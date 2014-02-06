import re

# regexpes used in functions:

# ( everything but `)` ) or lookahead for \s or end of line
tag_param_regexp = r'(\(([^)]*)\)|(?=(\s|$)))'
# prepend word (sequence without \s and `(`)
tag_regexp_without_at = r'[^\(\s]+' + tag_param_regexp
tag_pattern_without_at = re.compile(tag_regexp_without_at + r'\Z')
# prepend '@'
tag_pattern = re.compile('(?<!^)(@' + tag_regexp_without_at + ')')

#

def enclose_tags(text, prefix, postfix):
    """
    puts `prefix` before and `postfix` after
    every tag in text
    """
    def f(t):
        return prefix + t.group(1) + postfix
    return re.sub(tag_pattern, f, text)
