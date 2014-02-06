# -*- coding: utf-8 -*-
import sys
sys.path.append('/Users/bvsc/Dropbox/Projects')

from datetime import date
import re

# config
from todoflow.config import inbox_path
from todoflow.config import inbox_tag_to_path

def make_re(tag):
    return re.compile('(?:^|\s)(' + tag + ')(?:$|\s|\()')

url_pattern = re.compile('https{0,1}://\S*')


def add_tags(msg):
    return url_pattern.sub(lambda x: '@web(' + x.group(0) + ')', msg)


def inbox(msg):
    wtf = { # I dont know, I have strange problems with encoding in Sublime Text
        'ż': 'ż', # you can probably remove this
        'ę': 'ę',
        'ó': 'ó',
        'ą': 'ą',
        'ś': 'ś',
        'ń': 'ń',
        'ź': 'ź',
        'ć': 'ć',
        'ń': 'ń',
        'Ż': 'Ż',
        'Ó': 'Ó',
        'Ę': 'Ę',
        'Ą': 'Ą',
        'Ź': 'Ź',
        'Ń': 'Ń',
        'Ć': 'Ć',
        'Ś': 'Ś',
    }
    for k, v in wtf.items():
        msg = msg.replace(k, v)
    msg = ' ' + msg.strip().replace('\\n', '\n').replace('\\t', '\t')
    msg = add_tags(msg)
    to_write = "-" + msg + ' @in(' + date.today().isoformat() + ')'

    path_to_add = inbox_path

    for tag, path in inbox_tag_to_path.items():
        if make_re(tag).findall(msg):
            path_to_add = path

    with open(path_to_add, 'r') as f:
        old = f.read()
        if old and not old.endswith('\n'):
            to_write += '\n'
    with open(path_to_add, 'a') as f:
        print path_to_add
        f.write(to_write + '\n')

if __name__ == '__main__':
    inbox(' '.join(sys.argv[1:]))
