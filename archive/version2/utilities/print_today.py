#!/usr/bin/python
from config import should_print_path as should_print
import topy

t = topy.from_files(topy.lists.to_list())
today_not_done = t.filter('@today and not @done')
today_not_done.remove_tag('today')
if int(open(should_print).read()):
    print today_not_done.as_plain_text(colored=True, indent=False)
else:
    print ''
