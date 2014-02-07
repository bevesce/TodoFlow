#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sublime
import sublime_plugin
from datetime import datetime, date

import sys
sys.path.append('/path/to/parent/of/todoflow')  # TODO: find some better way to ensure that todoflow can be found on python path

import todoflow
from todoflow.printers import PlainPrinter3 as pp
import todoflow.src.utils as u


class MultipleLinesModifierCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line = self.view.line(region)
            text = self.view.substr(line).rstrip()
            rpl = self.modify(text)
            self.view.replace(edit, line, rpl)
        
        new_selections = []
        for sel in list(self.view.sel()):
            if not sel.empty():
                new_selections.append(sublime.Region(sel.b, sel.b))
            else:
                new_selections.append(sel)
        self.view.sel().clear()
        for sel in new_selections:
            self.view.sel().add(sel)


class TasksToggleCommand(MultipleLinesModifierCommand):
    def modify(sefl, text):
        """
        toggles between tags
        no_tag -> @next -> @working -> @done(date) -> no_tag
        """

        tags_to_toggle = ['next', 'working', 'done']
        tagged_already = False

        if u.has_tag(text, tags_to_toggle[-1]):
            text = u.remove_tag(text, tags_to_toggle[-1])
            tagged_already = True

        for i, tag in enumerate(tags_to_toggle[:-1]):
            if u.has_tag(text, tag):
                text = u.remove_tag(text, tag)
                text = u.add_tag(
                    text,
                    tags_to_toggle[i + 1],
                    param=date.today().isoformat() if tags_to_toggle[i + 1] == 'done' else None
                )
                tagged_already = True
                break
        if not tagged_already:
            text = u.add_tag(text, tags_to_toggle[0])
        return text


class NewTaskCommand(MultipleLinesModifierCommand):
    def modify(self, line):
        level = indent_level(line)
        if is_project(line):
            level += 1
        r = line + '\n' + '\t' * level + '- '
        return r


def indent_level(text):
    indent_char = u'\t'
    level = 0
    while level < len(text) and text[level] == indent_char:
        level += 1
    return level


class DateChangeCommand(sublime_plugin.TextCommand):
    def change_date(self, edit, change=1):
        # change date by `change` value,
        # what is changed (year, month, day)
        # depends on caret position
        for region in self.view.sel():
            old_date, date_region, what_selected = find_date(self.view, region)
            if what_selected == 'nothing':
                new_date = date.today()
            elif what_selected == 'day':
                new_date = old_date + timedelta(days=change)
            elif what_selected == 'month':
                month = old_date.month + change
                if month == 0:
                    month = 12
                if month == 13:
                    month = 1
                new_date = date(old_date.year, month, old_date.day)
            elif what_selected == 'year':
                new_date = date(old_date.year + change, old_date.month, old_date.day)
            new_date_str = '(' + new_date.isoformat() + ')'
            self.view.replace(edit, date_region, new_date_str)
            self.view.sel().subtract(date_region)
            self.view.sel().add(region)


class IncreaseDateCommand(DateChangeCommand):
    def run(self, edit):
        self.change_date(edit, change=1)


class DecreaseDateCommand(DateChangeCommand):
    def run(self, edit):
        self.change_date(edit, change=-1)



def find_date(view, region):
    max_iter = 20
    citer = 0
    start = region.begin()

    if (region.end() - region.begin()) == 0:
        x = view.substr(sublime.Region(region.begin(), region.end() + 1))
        if len(x) > 0 and x[-1] == '(':
            region = sublime.Region(region.begin() + 1, region.end() + 3)
        else:
            region = sublime.Region(region.begin() - 1, region.end())
    while view.substr(region)[-1] != ')' and view.substr(region)[-1] != '\n':
        citer += 1
        if citer > max_iter:
            break
        region = sublime.Region(region.begin(), region.end() + 1)
    while view.substr(region)[0] != '(' and view.substr(region)[0] != '\n':
        citer += 1
        if citer > max_iter:
            break
        region = sublime.Region(region.begin() - 1, region.end())
    date_str = view.substr(region).strip()

    # what was selcted depends on cursor position in date
    # `|` shows possible caret positions
    what = 'day'                     # |(2013-12-31)
    if start > region.begin():       # (|2|0|1|3|-12-31)
        what = 'year'
    if start > region.begin() + 5:   # (2013-|1|2|-31)
        what = 'month'
    if start > region.begin() + 8:   # (2013-12-|3|1|)
        what = 'day'
    if start > region.begin() + 11:  # (2013-12-31)|
        what = 'day'
    try:
        ddate = calc_date(date_str)
        return ddate, region, what
    except Exception as e:
        # calc_date fails when date was not selected,
        # so insert new one
        return date.today(), sublime.Region(start, start), 'nothing'


def calc_date(date_str):
    date_str = date_str[1:-1]
    return date(*(int(x) for x in date_str.split('-')))


class MoveToProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.tlist = todoflow.all_lists()
        self.projects = []
        self.ids = []
        for project in self.tlist.filter('type = "project"'):
            text = '\t' * project.indent_level + project.text
            self.projects.append(text)
            self.ids.append(project._id)

        self.view.window().show_quick_panel(self.projects, self.append_to_project)

    def append_to_project(self, index):
        if index == -1:
            return
        project_id = self.ids[index]
        for region in self.view.sel():
            line = self.view.line(region)
            text = self.view.substr(line).strip()
            items = text.split('\n')

            for item in items:
                item = strip(item)
                for titem in self.tlist:
                    if titem.text == item:
                        titem.remove_self_from_parent()
                todoflow.prepend_subtasks(project_id, item)

        todoflow.save(self.tlist)


def strip(text):
    text = text.strip()
    if text.startswith('- '):
        text = text[2:]
    if text.endswith(':'):
        text = text[:-1]
    return text