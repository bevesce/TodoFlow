"""
Main module, provides functions needes to
create TodoList object from plain text files
and operations that use items unique id like
tagging and removing.
"""

from todolist import TodoList, Task, Project
from todolist_parser import Parser
import fileslist as lists
from topy.config import quick_query_abbreviations as abbreviations
from topy.config import quick_query_abbreviations_conjuction as conjuction
import os.path
import subprocess
import todolist as todolist
from filterpredicate import TagPredicate


def from_file(path):
    return Parser.list_from_file(path)


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
        tlist = from_file(path)
        tlist.indent()
        # set file name as project title
        title = os.path.splitext(os.path.basename(path))[0] + ':'
        p = Project(line=title, sub_tasks=tlist)
        p.source = path  # set source to use in `save` function
        items.append(p)
    return TodoList(items)


def do(item_id):
    TodoList.do(item_id)


def tag(item_id, tag, param=None):
    TodoList.tag(item_id, tag, param)


def remove(item_id):
    TodoList.remove(item_id)


def get_content(item_id):
    return TodoList.get_content(item_id)


def tag_dependand_action(item_id):
    item = TodoList.get_item(item_id)
    if item.has_tag('@web'):
        action.open(item.get_tag_param('@web'))
    if item.has_tag('@file'):
        action.open(item.get_tag_param('@file'))
    if item.has_any_tags(['@download', '@tvseries']):
        action.alfread_search('pb ' + item.get_content())
    if item.has_any_tags(['@search', '@research']):
        action.alfread_search('g ' + item.get_content())
    action.put_to_clipboard(item.get_content())


class action():
    @staticmethod
    def open(to_open):
        subprocess.call('open "{0}"'.format(to_open), shell=True)

    @staticmethod
    def alfread_search(query):
        subprocess.call(
            'osascript -e "tell application \\"Alfred 2\\" to search \\"{0}\\""'.format(query),
            shell=True
        )

    @staticmethod
    def put_to_clipboard(text):
        subprocess.call('echo ' + text + ' | pbcopy', shell=True)


def add_new_subtask(item_id, new_item):
    """
    new_item should be item of type Task, Project, Note or
    string, in that case it's assumed that it's task
    """
    if isinstance(new_item, str):
        new_item = TodoList([Task('- ' + new_item)])
    TodoList.items_by_id[item_id].append_subtasks(new_item)


def expand_shortcuts(query):
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
            expanded_query.append(abbreviations[query[i]])
        expanded_query.append(query[first_space_idx + 1:])
        return conjuction.join(expanded_query)


def archive(tlist, archive_tlist=None):
    """
    moves @done items to first project of title Archive
    assumes that it exsits
    if `archive_tlist` is not specified puts archived items
    to itself
    """
    done = tlist.filter('@done and project != Archive', remove=True)
    done_list = done.deep_copy().flatten()
    if not archive_tlist:
        archive_tlist = tlist
    arch_id = archive_tlist.find_project_id_by_title('Archive')
    TodoList.items_by_id[arch_id].prepend_subtasks(TodoList(done_list))


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
            with open(item.source, 'w') as f:
                item.sub_tasks.indent(-1)
                f.write(item.sub_tasks.as_plain_text())
