from __future__ import absolute_import
import os
from .parser import parse
from .todos import Todos, Todonode


def from_text(text):
    return parse(text)


def from_path(path):
    with open(path, 'r') as f:
        text = f.read().decode('utf-8')
    todos = parse(text)
    todos.source = path
    return todos


def from_paths(paths):
    def _path_to_title(path):
        return os.path.splitext(os.path.split(path)[-1])[0]
    subtodos_collection = [from_path(p) for p in paths]
    project_titles_collection = [_path_to_title(p) for p in paths]
    items = []
    for project_title, subtodos in zip(project_titles_collection, subtodos_collection):
        subtodos.indent()
        node = Todonode(text=project_title, subtodos=subtodos)
        node.item.change_to_project()
        items.append(node)
    return Todos(items=items)
