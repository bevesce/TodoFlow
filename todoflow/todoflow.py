from __future__ import absolute_import
import os
import glob
from .parser import parse
from .todos import Todos
from .compatibility import read, write, unicode


def from_text(text):
    return parse(text)


def from_path(path):
    text = read(path)
    todos = parse(text)
    todos.set_source(path)
    return todos


def from_paths(paths):
    todos = Todos()
    for path in paths:
        subtodos = from_path(path)
        project_title = _get_project_title(path)
        subtodos.set_master_item(project_title)
        todos += subtodos
    return todos


def _get_project_title(path):
    filename = os.path.split(path)[1]
    return os.path.splitext(filename)[0] + ':'


def from_dir(path, extension='.taskpaper'):
    return from_paths(
        _list_files_in_dir(path, extension)
    )


def _list_files_in_dir(path, extension='.taskpaper'):
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(extension):
                yield os.path.join(root, filename)


def to_path(todos, path):
    write(path, unicode(todos))


def to_sources(todos):
    for subtodos in todos.iter_sourced():
        to_path(subtodos, subtodos.get_source())
