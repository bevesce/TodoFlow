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
from . import fileslist as lists
from .todolist import TodoList
from .item import Task, Project, NewLineItem
from .parser import Parser
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


def get_item(item_id):
    return TodoList.items_by_id[item_id]


def edit(item_id, new_content):
    TodoList.edit(item_id, new_content.decode('utf-8'))


def get_text(item_id):
    return TodoList.get_text(item_id)


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
    is_unicode = False
    try:
        is_unicode = isinstance(new_item, unicode)
    except NameError:
        pass

    if is_unicode or isinstance(new_item, str):
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
            try:
                f = open(item.source.strip(), 'w', encoding='utf-8', errors='ignore')
            except TypeError:
                f = open(item.source.strip(), 'w')
            item.sublist.dedent()
            text = PlainPrinter().pformat(item.sublist)
            f.write(text)
            f.close()

def editorial_save(tlist):
    """
    **This will fail horribly if used outside Editorial**
    It's not really save, only preparation to it.
    To use only in Editorial.app, it's workaround [this bug](http://omz-forums.appspot.com/editorial/post/5925732018552832)
    that doesn't allow to use simple call to editor.set_files_contents, instead it's required to use Set File Contents block.

    It's annoying.
    """
    import workflow
    import pickle
    paths = []
    path_to_content = {}
    for item in tlist.items: 
        if hasattr(item, 'source'):
            item.sublist.dedent()
            text = PlainPrinter().pformat(item.sublist)
            path = item.source.replace(path_to_folder_synced_in_editorial, '')
            paths.append(path)
            path_to_content[path] = text.decode('utf-8')
    with real_open('content-temp.pickle', 'w') as f:
        pickle.dump(path_to_content, f)
    workflow.set_output('\n'.join(paths))