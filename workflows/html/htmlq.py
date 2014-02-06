#!/usr/bin/python

import sys
sys.path.append('/Users/bvsc/Dropbox/Projects')

import todoflow
from todoflow.config import path_to_css
from todoflow.printers import HTMLPrinter, HTMLLinkedPrinter, EditorialPrinter

query = ' '.join(sys.argv[1:])
query = todoflow.expand_query(query)

t = todoflow.from_files(todoflow.lists.to_list()).filter(query)
HTMLLinkedPrinter(path_to_css).pprint(t)
