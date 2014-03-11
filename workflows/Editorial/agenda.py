#coding: utf-8
#!/usr/bin/python
import sys
import todoflow
import math
from todoflow.printers import EditorialPrinter

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

from datetime import datetime, date

title_length = 80




def htmlify(tag, text, classes=''):
    if not (isinstance(classes, str) or isinstance(classes, unicode)):
        classes = ' '.join(classes)
    return u'<{0} class="{1}">{2}</{0}>'.format(tag, classes, text)


def titleize(title, style):
    return htmlify('h1', title, ('section-title', style))


def print_query(t, title, query, style):
    s = EditorialPrinter().pformat(t.filter(query)).decode('utf-8')
    if s:
        return htmlify(
            'div',
            (titleize(title, style) + u'\n' + s),
            ['agenda-section', style + '-section']
        ).encode('utf-8')
    return ''


def calculate_days_left(item, tag):
    param = item.get_tag_param(tag)
    due_date = datetime.strptime(param, '%Y-%m-%d').date()
    days = (due_date - date.today()).days
    days_str = str(days).zfill(2)
    return days, days_str


def get_style_for_due(days_left, item):
    style = 'far-away'
    if item.has_tag('blocked'):
        style = 'blocked'
    elif days_left <= 2:
        style = 'soon'
    elif days_left <= 7:
        style = 'this-week'
    return ['countdown', style]

from todoflow.config import path_to_folder_synced_in_editorial


def make_linked_text(days_str, item):
    inside_link = htmlify('span', days_str, 'days-number') + ' ' + item.text
    file_url = item.source.replace(path_to_folder_synced_in_editorial, '')
    return u'<a href="editorial://open/{0}?root=dropbox&command=goto&input={2}:{3}">{1}</a>'.format(
                file_url, 
                inside_link, 
                item.first_char_no,
                item.first_char_no + \
                    len(item.text) + \
                    item.indent_level + \
                    (1 if item.type == 'task' else 0) + \
                    (-1 if item.type == 'note' else 0),
            )


def print_deadlines(t, tag, due, title_style, title):
    if not due:
        return
    dues = []
    for item in due:
        if item.has_tag(tag):
            text = enclose_tags(item.text, '<span class="tag">', '</span>')
            days, days_str = calculate_days_left(item, tag)
            style = get_style_for_due(days, item)
            linked_text = make_linked_text(days_str, item)
            dues.append((linked_text, style))
        else:
            pass
    result = titleize(title, title_style) + \
        htmlify('ul', '\n'.join([htmlify('li', text, style) for text, style in sorted(dues)]))
    return result.encode('utf-8')


def print_due(t):
    due = t.filter('@due and not @done and not project ? onhold')
    if not due.items:
          return
    return htmlify(
        'div',
        print_deadlines(t, 'due', due, 'deadlines', 'Deadlines'),
        ['agenda-section', 'deadlines-section']
    ).encode('utf-8')


def print_dates(t):
    due = t.filter('@date and not @done')
    if not  bool(due.items):
            return ''
    return htmlify(
        'div',
        print_deadlines(t, 'date', due, 'dates', 'Dates'),
        ['agenda-section', 'dates-section']
    ).encode('utf-8')
    


t = todoflow.from_files(todoflow.lists.to_list())

query_today = '@working and not @done'
query_next = '@next and not @done and not @working'

html_parts = [
    print_due(t),
    print_dates(t),
    print_query(t, 'Working', query_today, 'working'),
    print_query(t, 'Next', query_next, 'next'),
    '<a class="reload-button" id="reload-button" href="editorial://?command=TF:%20Agenda">Reload</a>',
]

action_out = '\n'.join(html_parts).decode('utf-8')

import workflow
workflow.set_output(action_out)

import editor
if editor.get_theme() == 'Dark':
    css = workflow.get_variable('dark css')
else:
    css = workflow.get_variable('light css')

workflow.set_variable('css', css.decode('utf-8'))
