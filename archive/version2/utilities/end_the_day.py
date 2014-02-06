#!/usr/bin/python
from config import projects_path, inbox_path, onhold_path  # archive_path
import topy
# from archive import archive
from update_lists import update_daily, update_weekly, update_waiting, update_followups
from remind import set_reminders
from tvcal import tvcal
from log_to_day_one import log_to_day_one

all_lists = topy.from_files(topy.lists.to_list())
inbox_file = open(inbox_path, 'a')
onhold_list = topy.from_file(onhold_path)

log_to_day_one(all_lists.deep_copy())
try:
    tvcal(inbox_file)
except:
    pass
update_weekly(onhold_list, inbox_file)
update_waiting(onhold_list, inbox_file)

update_daily(all_lists)
update_followups(all_lists)
set_reminders(all_lists)
topy.save(all_lists)
