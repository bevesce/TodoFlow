"""
module provides functions to store and retrieve paths of
files with todo lists
"""

# from alfredlist import AlfredItemsList
import os
from todoflow.config import files_list_path, files_list_name

full_path = files_list_path + files_list_name

def change_list(items, change_f):
    # load items from file
    previous = set()
    with open(full_path, 'r') as f:
        text = f.read()
        if text:
            previous = set(text.split('\n'))

    # change items from file using change_f function
    if isinstance(items, str):
        items = set(items.split('\n'))
    new = change_f(previous, items)

    with open(full_path, 'w') as f:
        f.write('\n'.join(new))


def add(items):
    change_list(items, lambda p, i: p.union(i))


def remove(items):
    change_list(items, lambda p, i: p - set(i))


def clear():
    with open(full_path, 'w') as f:
        f.write('')


def to_list():
    with open(full_path, 'r') as f:
        return [l for l in f.read().split('\n') if l]
