#!/usr/bin/python

import argparse
import sys
import subprocess
import topy

parser = argparse.ArgumentParser(
    description='Open page with todo list in default browser.')

parser.add_argument(
    '-q', '--query',
    type=str,
    action='store',
    nargs=1,
    default=[''],
    help='predicate to filter with'
)

parser.add_argument(
    '-p', '--paths',
    type=str,
    action='store',
    nargs='*',
    default=topy.lists.to_list(),
    help="paths to files containg todo list, "
         "defaults to paths stored in topy.lists "
         "(see config.py)"
)

parser.add_argument(
    '--css',
    type=str,
    action='store',
    nargs=1,
    default=None,
    help="css stylesheet, only valid with --html"
    )


args = parser.parse_args()
tlist = topy.from_files(args.paths)
filtered = tlist.filter(args.query[0])
css_style = args.css[0]

def open_html(tlist, css_style=None):
    html = tlist.as_full_html(css_style=css_style)
    with open('html/temp.html', 'w') as f:
        f.write(html)
    subprocess.call('open html/temp.html', shell=True)

open_html(filtered, css_style=css_style)
