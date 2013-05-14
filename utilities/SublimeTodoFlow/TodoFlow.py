#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sublime_plugin, sublime
from datetime import date, timedelta


settings = sublime.load_settings('TodoFlow.sublime-settings')


append_date_to_done = settings.get("append_date_to_done")
today_tag = settings.get("today_tag")
done_tag = settings.get("done_tag")
next_tag = settings.get("next_tag")
excluded_tags = settings.get("excluded_tags")
allways_included_tags = settings.get("allways_included_tags")
default_date_increase = settings.get("default_date_increase")


def is_task(line):
    return line.strip()[0:2] == '- '

# ( everything but `)` ) or lookahead for \s or end of line
tag_param_regexp = r'(\(([^)]*)\)|(?=(\s|$)))'
# prepend word (sequence without \s and `(`)
tag_regexp_without_at = r'[^\(\s]*' + tag_param_regexp
tag_pattern_without_at = re.compile(tag_regexp_without_at)
tag_pattern = re.compile('(@' + tag_regexp_without_at + ')')

next_tag_pattern = re.compile(r'@' + next_tag + r'(?=(\s|$))')
done_tag_pattern = re.compile(r'@' + done_tag + r'(\(([^)]*)\)|(?=(\s|$)))')
today_tag_pattern = re.compile(r'@' + today_tag + r'(?=(\s|$))')


def is_project(line):
    splitted = line.split(':')
    if len(splitted) < 2:  # no `:` in line
        return False
    if line[-1] == u' ':  # trailing space after `:`
        return False
    if splitted[1].strip() != '' and splitted[1].strip()[0] != '@':
        return False
    # only tags are allowed after `:`
    after_colon = splitted[-1].split(u'@')
    only_tags_after_colon = all([
        tag_pattern_without_at.match(tag) for tag in after_colon
    ])
    return only_tags_after_colon


def indent_level(text):
    indent_char = u'\t'
    level = 0
    while level < len(text) and text[level] == indent_char:
        level += 1
    return level


class TaskCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        work_on_file(self, edit)

    def process(self, line):
        if re.search(next_tag_pattern, line):
            line = next_tag_pattern.sub('@' + today_tag, line)
        elif re.search(today_tag_pattern, line):
            line = today_tag_pattern.sub(
                '@' + done_tag +
                ('({0})'.format(date.today().isoformat()) if append_date_to_done else ''),
                line
            )
        elif re.search(done_tag_pattern, line):
            line = done_tag_pattern.sub('', line)
        else:
            if line[-1] != ' ':
                line += ' '
            line += '@' + next_tag
        if line[-1] == ' ':
            line = line[0:-1]
        return line


class NewTaskCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        work_on_file(self, edit)

    def process(self, line):
        level = indent_level(line)
        if is_project(line):
            level += 1
        return line + '\n' + '\t' * level + '- '


class ChangeTypeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        work_on_file(self, edit)

    def process(self, line):
        level = indent_level(line)
        if is_task(line):  # change to project
            print 'task'
            line = '\t' * level + line.strip()[2:]

            # insert `:` before trailing tags
            splitted = line.split(' @')
            last_trailing_tag_idx = len(splitted) - 1
            if last_trailing_tag_idx == 0:
                return line + ':'
            while tag_pattern_without_at.match(
                splitted[last_trailing_tag_idx]
            ) and last_trailing_tag_idx > 1:
                last_trailing_tag_idx -= 1

            line = ' @'.join(splitted[0:last_trailing_tag_idx]) + ':'
            if len(splitted[last_trailing_tag_idx:]):
                line += ' @' + ' @'.join(splitted[last_trailing_tag_idx:])

        elif is_project(line):  # change to note
            print 'project'
            splitted = [s for s in line.split(':') if s.strip()]
            line = ':'.join(splitted[0:-1]) + splitted[-1]
            print 'project new:'

        else:  # change to task
            print 'note'
            return '\t' * level + '- ' + line.strip()

        if line[-1] == ' ':
            line = line[0:-1]
        return line


def is_banned_tag(tag):
    for b in [t + '(' for t in excluded_tags]:
        if tag.startswith(b):
            return True
    for b in [t in excluded_tags]:
        if b == tag:
            return True


class AddTagCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        text = self.view.substr(sublime.Region(0, self.view.size()))
        # find all tags in text
        ## find tags with parameters
        self.tags_list = re.findall(' @[^\(\s]*\([^)]*\)', text)
        ## find tags without parameters
        self.tags_list += re.findall(' @[^\(\s]*\s', text)
        ## strip tags
        self.tags_list = [tag[2:].strip() for tag in self.tags_list]
        ## exlude excluded tags
        self.tags_list = [tag for tag in self.tags_list if not is_banned_tag(tag)]
        ## add versions of tags without parameter
        self.tags_list += [tag[0:tag.find('(')] for tag in self.tags_list if '(' in tag]
        ## add allways included tags
        self.tags_list += allways_included_tags
        ## remove duplicates
        self.tags_list = list(set(self.tags_list))
        # show tags
        self.view.window().show_quick_panel(self.tags_list, self.on_selection)

    def on_selection(self, selection):
        work_on_file(self, self.edit, selection)

    def process(self, line, selection):
        if selection == -1:
            return line
        if line[-1] != ' ':
            line += ' '
        return line + '@' + self.tags_list[selection]


def work_on_file(self, edit, *args):
    # process every line in selection
    # and replace it with result
    for region in self.view.sel():
        line_region = self.view.line(region)
        line = self.view.substr(line_region)
        lines = line.split('\n')
        processed_line = '\n'.join([self.process(each_line, *args) for each_line in lines])
        if processed_line != line:
            self.view.replace(edit, line_region, processed_line)


class IncreaseDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        change_date(self.view, edit, change=1)


def change_date(view, edit, change=1):
    # change date by `change` value,
    # what is changed (year, month, day)
    # depends on cursor position
    for region in view.sel():
        old_date, date_region, what_selected = find_date(view, region)
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
        view.replace(edit, date_region, new_date_str)
        view.sel().subtract(date_region)
        view.sel().add(region)


def find_date(view, region):
    max_iter = 20
    citer = 0
    start = region.begin()

    if (region.end() - region.begin()) == 0:
        x = view.substr(sublime.Region(region.begin(), region.end() + 1))
        if len(x) > 0 and x[-1] == '(':
            print x
            region = sublime.Region(region.begin() + 1, region.end() + 3)
            print view.substr(region)
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
    # `|` shows possible cursor positions
    what = default_date_increase     # |(2013-12-31)
    if start > region.begin():       # (|2|0|1|3|-12-31)
        what = 'year'
    if start > region.begin() + 5:   # (2013-|1|2|-31)
        what = 'month'
    if start > region.begin() + 8:   # (2013-12-|3|1|)
        what = 'day'
    if start > region.begin() + 11:  # (2013-12-31)|
        what = default_date_increase
    try:
        ddate = calc_date(date_str)
        return ddate, region, what
    except Exception as e:
        # calc_date fails when date was not selected,
        # so insert new one
        print e
        return date.today(), sublime.Region(start, start), 'nothing'


def calc_date(date_str):
    date_str = date_str[1:-1]
    return date(*(int(x) for x in date_str.split('-')))


class DecreaseDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        change_date(self.view, edit, change=-1)
