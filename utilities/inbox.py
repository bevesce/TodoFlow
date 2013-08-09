#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from datetime import date
from config import inbox_path, inbox_tag_to_path
import re


def make_re(tag):
    return re.compile('(?:^|\s)(' + tag + ')(?:$|\s)')


def inbox(msg):
    if msg[0] != ' ':
        msg = ' ' + msg
    if msg[-1] != ' ':
        msg += ' '
    to_write = '-' + msg + '@in(' + date.today().isoformat() + ')\n'
    path_to_add = inbox_path
    for tag, path in inbox_tag_to_path.items():
        if make_re(tag).findall(msg):
            path_to_add = path
    with open(path_to_add, 'a') as f:
        f.write(to_write + '\n')

if __name__ == '__main__':
    inbox(" ".join(sys.argv[1:]))
