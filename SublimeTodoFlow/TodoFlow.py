#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sublime_plugin, sublime
from datetime import date


def is_task(line):
    return line.strip()[0:2] == '- '

tag_pattern_without_at = re.compile(ur'[^\(\s]*(|\([^)]*\))')
tag_pattern = re.compile(ur'@[^\(\s]*(\([^)]*\)|)')

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
        for region in self.view.sel():
            line_region = self.view.line(region)
            line = self.view.substr(line_region)
            lines = line.split('\n')
            processed_line = '\n'.join([self.process(each_line) for each_line in lines])
            if processed_line != line:
                self.view.replace(edit, line_region, processed_line)

    def process(self, line):
        if re.search(u' @next(\s|$)', line):
            line = re.sub(' @next', ' @today', line)
        elif '@today' in line:
            line = re.sub(' @today', ' @done({0})'.format(date.today().isoformat()), line)
        elif '@done(' in line:
            line = re.sub(r'@done\(.*\)', '', line)
        else:
            if line[-1] != ' ':
                line += ' '
            line += '@next'
        if line[-1] == ' ':
            line = line[0:-1]
        return line


class NewTaskCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            line = self.view.substr(line_region)
            lines = line.split('\n')
            processed_line = '\n'.join([self.process(each_line) for each_line in lines])
            if processed_line != line:
                self.view.replace(edit, line_region, processed_line)

    def process(self, line):
        level = indent_level(line)
        if is_project(line):
            level += 1
        return line + '\n' + '\t' * level + '- '


class ChangeTypeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            line = self.view.substr(line_region)
            lines = line.split('\n')
            processed_line = '\n'.join([self.process(each_line) for each_line in lines])
            if processed_line != line:
                self.view.replace(edit, line_region, processed_line)

    def process(self, line):
        level = indent_level(line)
        if is_task(line):
            line = '\t' * level + line.strip()[2:]
            splitted = line.split(' @')
            idx = len(splitted) - 1
            if idx == 0:
                return line + ':'
            while tag_pattern_without_at.match(splitted[idx]) and idx > 1:
                idx -= 1
            print idx
            line = ' @'.join(splitted[0:idx]) + ':'
            if len(splitted[idx:]):
                line += ' @' + ' @'.join(splitted[idx:])
        elif is_project(line):
            line = re.sub(':($|\s)', ' ', line)
        else:
            return '\t' * level + '- ' + line.strip()
        if line[-1] == ' ':
            line = line[0:-1]
        return line


def banned_tag(tag):
    banned = ['project(', 'due(', 'done(', 'in(']
    for b in banned:
        if tag.startswith(b):
            return True


class AddTagCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        text = self.view.substr(sublime.Region(0, self.view.size()))
        self.tags_list = re.findall('@[^\(\s]*\([^)]*\)', text)
        self.tags_list += re.findall('@[^\(\s]*\s', text)
        self.tags_list = [tag[1:].strip() for tag in self.tags_list]
        self.tags_list = [tag for tag in self.tags_list if not banned_tag(tag)]
        self.tags_list = list(set(self.tags_list))
        self.view.window().show_quick_panel(self.tags_list, self.on_selection)

    def on_selection(self, selection):
        for region in self.view.sel():
            line_region = self.view.line(region)
            line = self.view.substr(line_region)
            lines = line.split('\n')
            processed_line = '\n'.join([self.process(each_line, selection) for each_line in lines])
            if processed_line != line:
                self.view.replace(self.edit, line_region, processed_line)

    def process(self, line, selection):
        if selection == -1:
            return line
        if line[-1] != ' ':
            line += ' '
        return line + '@' + self.tags_list[selection]
