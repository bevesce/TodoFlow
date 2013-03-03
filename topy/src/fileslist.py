"""
module provides functions to store and retrieve paths of
files with todo lists
"""

from alfredlist import AlfredItemsList
import os
from topy.config import files_list_path, files_list_name

dir_path = os.path.expanduser(files_list_path)
# create directory if it doesn't exist
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)
full_path = dir_path + files_list_name
# create `selection` file if it doesn't exist
try:
    open(full_path, 'r')
except IOError:
    open(full_path, 'w').close()


def change_list(items, change_f):
    # load items from file
    previous = set()
    with open(full_path, 'r') as f:
        text = f.read()
        if text:
            previous = set(text.split('\t'))

    # change items from file using change_f function
    if isinstance(items, str):
        items = set(items.split('\t'))
    new = change_f(previous, items)

    with open(full_path, 'w') as f:
        f.write('\t'.join(new))


def add(items):
    change_list(items, lambda p, i: p.union(i))


def remove(items):
    change_list(items, lambda p, i: p - set(i))


def clear():
    with open(full_path, 'w') as f:
        f.write('')


def to_alfred_xml(query):
    items = None
    with open(full_path, 'r') as f:
        text = f.read()
        if text:
            items = set(text.split('\t'))

    if not items:
        return  # alfred will display "Please wait" subtext

    al = AlfredItemsList()
    # add selected files
    for item in items:
        if query.lower() in item.lower():
            al.append(
                arg=item,
                title='/'.join(item.split('/')[-2:]),
                subtitle='',
                icon='remove'.format(item))
    return al


def to_list():
    with open(full_path, 'r') as f:
        return f.read().split('\t')
