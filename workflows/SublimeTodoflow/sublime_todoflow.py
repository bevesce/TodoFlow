import sublime
import sublime_plugin
import datetime as dt

import sys
import os
sys.path.append(
    '/usr/local/lib/python3.4/site-packages'
)

from . import todoflow
from .todoflow import textutils as tu


def settings():
    return sublime.load_settings('Todoflow.sublime-settings')


class ModifySelectedLinesCommand(sublime_plugin.TextCommand):
    def modify_selected_lines(self, edit, modification, move_selection_to_end=True):
        selection = self.view.sel()
        ends_of_lines = []
        for region in selection:
            line_boundries = self.view.line(region)
            line_text = self.view.substr(line_boundries)
            new_text = modification(line_text, region, line_boundries, selection)
            ends_of_lines.append(self._calculate_end_of_line_region(region, new_text))
            self.view.replace(edit, line_boundries, new_text)
        if move_selection_to_end:
            self._set_new_selections(selection, ends_of_lines)

    def _calculate_end_of_line_region(self, region, new_text):
        line = self.view.line(region)
        new_region = sublime.Region(line.a + len(new_text), line.a + len(new_text))
        return new_region

    def _set_new_selections(self, selection, new_selections):
        selection.clear()
        selection.add_all(new_selections)


class ToggleTagsCommand(ModifySelectedLinesCommand):
    def run(self, edit):
        self.modify_selected_lines(edit, self.toggle_tags)

    def toggle_tags(self, text, region, line_boundries, selection):
        tags = settings().get('tags_to_toggle', [('done', None)])
        print(text, tags)
        return tu.toggle_tags(text, tags)


class ChangeDateCommand(ModifySelectedLinesCommand):
    date_format = '%Y-%m-%d'
    date_length = len(dt.datetime.now().strftime(date_format))

    def run(self, edit):
        self.modify_selected_lines(edit, self.change_date, move_selection_to_end=False)

    def change_date(self, text, region, line_boundries, selection):
        selection_start = region.a - line_boundries.a
        date, date_start = self._find_date(text, selection_start)
        if date:
            new_text = self._change_date_text(text, region, date, date_start)
        else:
            new_text = self._insert_date(text, selection_start)
        return new_text

    def _find_date(self, text, index):
        for i in range(index - self.date_length, index + self.date_length):
            try:
                return dt.datetime.strptime(text[i:i + self.date_length], self.date_format), i
            except ValueError as e:
                pass
        return None, None

    def _change_date_text(self, text, region, date, date_start):
        new_date = self._change_date(date)
        return text[:date_start] + new_date.strftime(self.date_format) + text[date_start + self.date_length:]

    def _change_date(self, date):
        raise NotImplemented

    def _insert_date(self, text, selection_start):
        date_as_text = dt.datetime.now().strftime(self.date_format)
        return text[:selection_start] + date_as_text + text[selection_start:]

    def _caret_in_parenthesis(self, text, caret_position):  # currenly unused...
        if caret_position >= len(text):
            return False
        return text[caret_position - 1] == '(' and text[caret_position] == ')'


class IncreaseDateCommand(ChangeDateCommand):
    def _change_date(self, date):
        return date + dt.timedelta(days=1)


class DecreaseDateCommand(ChangeDateCommand):
    def _change_date(self, date):
        return date - dt.timedelta(days=1)


class MoveToProject(ModifySelectedLinesCommand):
    def run(self, edit):
        self.edit = edit
        self.prep_path()
        self.prep_lines()
        self.prep_todos()
        self.show_projects_panel()

    def prep_path(self):
        self.path = self.view.file_name()

    def prep_lines(self):
        self.lines = []
        selections = self.view.sel()
        for sel in selections:
            for line in self.view.lines(sel):
                self.lines.append((
                    self.view.rowcol(line.a)[0],
                    self.view.substr(line)
                ))

    def prep_todos(self):
        self.todos = todoflow.from_dir(settings().get('todos_dir_path'))

    def show_projects_panel(self):
        query = 'type = "project"'
        self.projects = tuple(self.todos.search(query))
        self.projects_texts = str(self.todos.filter(query)).splitlines()
        self.view.window().show_quick_panel(
            self.projects_texts,
            self.append_to_project
        )

    def append_to_project(self, selected_index):
        if selected_index == -1:
            return
        changed_todos = self.todos
        for linenum, line_text in self.lines:
            # remove from current place
            changed_todos = changed_todos.filter(
                'not (source = {} and linenum = {})'.format(self.path, linenum)
            )
            changed_todos = changed_todos.by_prepending(
                line_text,
                to_item=self.projects[selected_index]
            )
        todoflow.to_sources(changed_todos)
