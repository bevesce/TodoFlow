#coding: utf-8
#!/usr/bin/python
import sys
import todoflow
import math
from todoflow.src.printers import PythonistaPrinter
from datetime import date, datetime
import re
import console


def print_title(title, color):
    console.set_font(size=32)
    console.set_color(*color)
    print title
    console.set_font()
    console.set_color()


def print_query(t, title, query, color):
    print_title(title, color)
    PythonistaPrinter().pprint(t.filter(query))


def calculate_days_left(item, tag):
    param = item.get_tag_param(tag)
    due_date = datetime.strptime(param, '%Y-%m-%d').date()
    days = (due_date - date.today()).days
    days_str = str(days).zfill(2)
    return days, days_str


def get_color(days_left, item):
    color = ()
    if item.has_tag('blocked'):
        color = (0.4, 0.4, 0.4)
    elif days_left <= 2:
        color = (1.0, 0.1, 0.1)
    elif days_left <= 7:
        color = (0.5, 0.5, 0.5)
    return color


def hcs(font_size=None, color=None):
    if font_size:
        console.set_font('', font_size)
    else:
        console.set_font()
    if color:
        console.set_color(*color)
    else:
        console.set_color()



def print_deadlines(t, query, tag, title_style, title):
    due = t.filter(query)
    if not due:
        return
    dues = []
    for item in due:
        if item.has_tag(tag):
            text = item.text
            days, days_str = calculate_days_left(item, tag)
            dues.append((days_str, text, get_color(days, item)))
        else:
            pass
    print_title(title, title_style)
    for days, text, color in dues:
        hcs(20)
        print days, hcs(color=color), text
        hcs()


t = todoflow.from_files(todoflow.lists.to_list())

query_today = '@working and not @done'
query_next = '@next and not @done and not @working'

print_deadlines(t, '@due and not @done and not @waiting', '@due', (1.0, 0.0, 0.0), 'Deadlines')
print_deadlines(t, '@date and not @done and not @waiting', '@date', (1.0, 1.0, 0.0), 'Dates')
print_query(t, 'Working', query_today, (0.0, 1.0, 1.0))
print_query(t, 'Next', query_next, (0.0, 0.0, 1.0))