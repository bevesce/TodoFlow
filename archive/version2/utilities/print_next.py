#!/usr/bin/python
from config import should_print_path as should_print
import topy

t = topy.from_files(topy.lists.to_list())
next = t.filter('@next and not @done and not @today and not project = onhold')
next.remove_tag('next')
if int(open(should_print).read()):
    print next.as_plain_text(colored=True, indent=False)
else:
    print ''

