#!/usr/bin/python
import sys
sys.path.append('/Users/bvsc/Dropbox/Projects')

import todoflow
from todoflow.printers import ColorPrinter

query = ' '.join(sys.argv[1:])
query = todoflow.expand_query(query)

t = todoflow.from_files(todoflow.lists.to_list()).filter(query)
print query
print '_' * len(query) + '\n'
ColorPrinter().pprint(t)
print ''
