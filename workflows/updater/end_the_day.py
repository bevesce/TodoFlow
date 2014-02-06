#!/usr/bin/python
import sys
sys.path += ['/Users/bvsc/Dropbox/Projects/todoflow/']
sys.path += ['/Users/bvsc/Dropbox/Projects/']
from todoflow.config import projects_path, inbox_path, onhold_path  # archive_path
import todoflow
import update_lists as ul

try:
    from tvcal import tvcal
except:
    pass
from log_to_day_one import log_to_day_one

all_lists = todoflow.from_files(todoflow.lists.to_list())
inbox_file = open(inbox_path, 'a')
onhold_list = todoflow.from_file(onhold_path)

log_to_day_one(all_lists.deep_copy())
try:
    tvcal(inbox_file)
except:
    pass
ul.update_weekly(onhold_list, inbox_file)
ul.update_waiting(onhold_list, inbox_file)

ul.update_daily(all_lists)
ul.update_followups(all_lists)
ul.update_blocked(all_lists)
ul.update_incremental(all_lists)
todoflow.save(all_lists)
