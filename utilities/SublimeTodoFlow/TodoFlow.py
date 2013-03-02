#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sublime_plugin, sublime
from datetime import date


def is_task(line):
    return line.strip()[0:2] == '- '

# ( everything but `)` ) or lookahead for \s or end of line
tag_param_regexp = r'(\(([^)]*)\)|(?=(\s|$)))'
# prepend word (sequence without \s and `(`)
tag_regexp_without_at = r'[^\(\s]*' + tag_param_regexp
tag_pattern_without_at = re.compile(tag_regexp_without_at)
tag_pattern = re.compile('(@' + tag_regexp_without_at + ')')

next_tag = re.compile(r'@next(?=(\s|$))')
done_tag = re.compile(r'@done(\(([^)]*)\)|(?=(\s|$)))')
today_tag = re.compile(r'@today(?=(\s|$))')


def is_project(line):
    splitted = line.split(':')
    if len(splitted) < 2:  # no `:` in line
        return False
    if line[-1] == u' ':  # trailing space after `:`
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
        if re.search(next_tag, line):
            line = next_tag.sub('@today', line)
        elif re.search(today_tag, line):
            line = today_tag.sub(
                '@done({0})'.format(date.today().isoformat()),
                line
            )
        elif re.search(done_tag, line):
            line = done_tag.sub('', line)
        else:
            if line[-1] != ' ':
                line += ' '
            line += '@next'
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
            line = re.sub(':(?=($|\s))', '', line)

        else:  # change to task
            return '\t' * level + '- ' + line.strip()

        if line[-1] == ' ':
            line = line[0:-1]
        return line


def is_banned_tag(tag):
    banned = ['project(', 'due(', 'done(', 'in(']
    for b in banned:
        if tag.startswith(b):
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
        ## exluce banned tags
        self.tags_list = [tag for tag in self.tags_list if not is_banned_tag(tag)]
        ## add versions of tags without parameter
        self.tags_list += [tag[0:tag.find('(')] for tag in self.tags_list if '(' in tag]
        ## remove duplicates
        self.tags_list = list(set(self.tags_list))
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
    for region in self.view.sel():
        line_region = self.view.line(region)
        line = self.view.substr(line_region)
        lines = line.split('\n')
        processed_line = '\n'.join([self.process(each_line, *args) for each_line in lines])
        if processed_line != line:
            self.view.replace(edit, line_region, processed_line)
