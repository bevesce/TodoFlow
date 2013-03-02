#!/usr/bin/python
from config import should_print_path as should_print
import topy

t = topy.from_files(topy.lists.to_list())
s = sorted(
    t.as_countdown(colored=True).split('\n')
    )[0:5]

if int(open(should_print).read()):
    print '\n'.join(s)
else:
    print ''
