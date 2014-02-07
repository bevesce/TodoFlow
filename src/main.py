# -*- coding: utf-8 -*-

"""
Main module, provides functions needes to
create TodoList object from plain text files
and operations that use items unique id like
tagging and removing.
"""

import os.path
import re
import subprocess
from datetime import datetime
import fileslist as lists
from todolist import TodoList
from item import Task, Project, NewLineItem
from parser import Parser
from todoflow.config import quick_query_abbreviations as abbreviations
from todoflow.config import quick_query_abbreviations_conjuction as conjuction
from todoflow.config import files_list_path, should_expand_dates, should_expand_shortcuts
from todoflow.printers import PlainPrinter



def all_lists():
    return from_files(lists.to_list())


def from_file(path):
    return Parser.list_from_file(path.strip())


def from_files(paths):
    """
    Constructs todolist from many files,
    content of the file is inserted to project that has
    file name as title

    paths - collection of path or tab separated string
    """
    if isinstance(paths, str):
        paths = paths.split('\t')
    items = []
    for path in paths:
        path = path.rstrip()
        tlist = TodoList([NewLineItem()]) + from_file(path)
        tlist.indent()
        # set file name as project title
        title = os.path.splitext(os.path.basename(path))[0] + ':'
        p = Project(text=title, sublist=tlist)
        p.source = path  # set source to use in `save` function
        p.set_source(path)
        items.append(p)
    return TodoList(items)


def from_text(text):
    return Parser.list_from_text(text)


def do(item_id):
    TodoList.do(item_id)


def tag(item_id, tag, param=None):
    TodoList.tag(item_id, tag, param)


def remove(item_id):
    TodoList.remove(item_id)


def edit(item_id, new_content):
    TodoList.edit(item_id, new_content.decode('utf-8'))


def get_text(item_id):
    return TodoList.get_text(item_id)


def tag_dependent_action(item_id):
    item = TodoList.get_item(item_id)
    to_open = ('@mail', '@web', '@file')
    for tag in to_open:
        if item.has_tag(tag):
            action.open(item.get_tag_param(tag))

    content = item.get_content()
    if item.has_any_tags(['@download', '@tvseries', '@comics']):
        action.alfred_search('pb ' + content)
    if item.has_any_tags(['@search', '@research']):
        action.alfred_search('g ' + content)
    action.put_to_clipboard(content)


class action():
    @staticmethod
    def open(to_open):
        try:
            subprocess.check_output('open "{0}"'.format(to_open), shell=True)
        except:
            to_open = files_list_path + to_open
            to_open = os.path.expanduser(to_open)
            subprocess.call('open "{0}"'.format(to_open), shell=True)

    @staticmethod
    def alfred_search(query):
        subprocess.call(
            'osascript -e "tell application \\"Alfred 2\\" to search \\"{0}\\""'.format(query),
            shell=True
        )

    @staticmethod
    def put_to_clipboard(text):
        subprocess.call('echo ' + text + ' | pbcopy', shell=True)


def append_subtasks(item_id, new_item):
    """
    new_item should be item of type Task, Project, Note or
    string, in that case it's assumed that it's task
    """
    if isinstance(new_item, unicode) or isinstance(new_item, str):
        new_item = TodoList([Task(new_item)])
    TodoList.items_by_id[item_id].append_subtasks(new_item)

add_new_subtask = append_subtasks


def prepend_subtasks(item_id, new_item):
    """
    new_item should be item of type Task, Project, Note or
    string, in that case it's assumed that it's task
    """
    if isinstance(new_item, unicode) or isinstance(new_item, str):
        new_item = TodoList([Task(new_item)])
    TodoList.items_by_id[item_id].prepend_subtasks(new_item)


def expand_shortcuts(query):
    if not should_expand_shortcuts:
        return query
    if query == '':
        return ''
    if query[0] == ' ':  # no abbreviations
        return query.strip()
    else:
        expanded_query = []
        # expand abbreviations till first space
        first_space_idx = query.find(' ')
        if first_space_idx == -1:
            first_space_idx = len(query)

        for i in range(0, first_space_idx):
            if not query[i] in abbreviations:
                return query.strip()
            expanded_query.append(abbreviations[query[i]])
        reminder = query[first_space_idx + 1:].strip()
        if reminder:
            expanded_query.append(reminder)
        return conjuction.join(expanded_query)


def expand_dates(query):
    if not should_expand_dates:
        return query
    pdt = None
    try:
        import parsedatetime as pdt
    except ImportError:
        pass
    if pdt:
        c = pdt.Constants()
        c.BirthdayEpoch = 80
        p = pdt.Calendar(c)
        def f(t):
            return datetime(*p.parse(query)[0][:6]).isoformat()
        return re.sub(r'\{[^}]*\}', f, query)
    else:
        return query


def expand_query(query):
    return expand_dates(expand_shortcuts(query))


def save(tlist):
    """
    Use to save changes to individual files of todolist constructed
    by `from_files` function.

    At the moment it's inefficient - function rewrites every file,
    even if todo list from it wasn't modified. If I notice that
    it has influence on workflow I'll improve this.
    """
    for item in tlist.items:
        if hasattr(item, 'source'):
            with open(item.source.strip(), 'w') as f:
                item.sublist.dedent()
                f.write(PlainPrinter().pformat(item.sublist))
