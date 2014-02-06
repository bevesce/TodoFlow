#!/usr/bin/python
import sys
sys.path.append('/Users/bvsc/Dropbox/Projects')

"""defines colors used in output"""
defc         = '\033[0m'

red          = '\033[1;31m'
green        = '\033[1;32m'
gray         = '\033[1;30m'
blue         = '\033[1;34m'

yellow       = '\033[1;33m'
magenta      = '\033[1;35m'
cyan         = '\033[1;36m'
white        = '\033[1;37m'
crimson      = '\033[1;38m'

high_red     = '\033[1;41m'
high_green   = '\033[1;42m'
high_brown   = '\033[1;43m'
high_blue    = '\033[1;44m'
high_magenta = '\033[1;45m'
high_cyan    = '\033[1;46m'
high_gray    = '\033[1;47m'
high_crimson = '\033[1;48m'

import todoflow
import math
from todoflow.printers import ColorPrinter
from datetime import datetime, date

title_length = 80

def titleize(title, high, color):
    spaces_no = title_length - len(title)
    return '\n' +  high + color + ' ' * int(math.floor(spaces_no / 2.)) + title + ' ' * int(math.ceil(spaces_no / 2.)) + defc + '\n'


def print_query(t, title, query, high, color):
    s = ColorPrinter().pformat(t.filter(query))
    if s:
        print titleize(title, high, color)
        print s

def print_due(t):
    print_deadlines(t, 'due', '@due and not @done and not project ? onhold', red, high_red, 'DEADLINES')

def print_dates(t):
    print_deadlines(t, 'date', '@date and not @done', magenta, high_magenta, 'DATES')

def print_deadlines(t, tag, query, highlight_color, title_color, title):
    due = t.filter(query)
    dues = []
    if due.items:
        print titleize(title, title_color, white)
    for item in due:
        if item.has_tag(tag):
            param = item.get_tag_param(tag)
            due_date = datetime.strptime(param, '%Y-%m-%d').date()
            days = (due_date - date.today()).days
            days_str = str(days).zfill(2)
            color = white
            if item.has_tag('blocked'):
                color = gray
            elif days <= 2:
                color = highlight_color
            elif days <= 7:
                color = yellow
            dues.append((days_str + ' ' + item.text + defc, color))
        else:
            # print '\t' * item.indent_level + gray + item.text + defc
            pass
    for d, c in sorted(dues):
        print c + d

t = todoflow.from_files(todoflow.lists.to_list())
print '\n' * 50

print_due(t)
print_dates(t)

query_today = '@working and not @done'
print_query(t, 'WORKING', query_today, high_green, white)

query_next = '@next and not @done and not @working'
print_query(t, 'NEXT', query_next, high_blue, white)
