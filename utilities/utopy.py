#!/usr/bin/python
import itopy as topy
from seamless_dropbox import open
import uuid
from datetime import date, timedelta
import os.path
# import sys
# sys.path += ['/Users/bvsc/Dropbox/TODO/scripts/topy/']

###################### Paths ######################

inbox_path = '/Users/bvsc/Dropbox/TODO/Inbox.todo'
projects_path = '/Users/bvsc/Dropbox/TODO/Projects.todo'
onhold_path = '/Users/bvsc/Dropbox/TODO/Onhold.todo'

###################################################


###################################################

################## log to day one #################

logging_in_day_one_for_yesterday = True

# change if you store Day One entries somewhere else
day_one_dir_path = os.path.expanduser(
    '~/Dropbox/Apps/Day One/Journal.dayone/entries/'
)

# title of entry
day_one_entry_title = '# Things I did today #\n\n\n'

day_one_extension = '.doentry'

###################################################

################## update lists ###################

# you can translate it to other language or something
# preserve order
days_of_the_week = (
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
)

# title of projects that contains tasks that
# shoul be do every day
daily_project_title = 'Daily'

# shoul remove waiting tasks that were moved to
# projects.todo form onhold.todo?
remove_waiting_from_onhold = False

###################################################





def log_to_day_one(tlist):
    uid = str(uuid.uuid1()).replace('-', '').upper()
    log_date = date.today()
    if logging_in_day_one_for_yesterday:
        log_date -= timedelta(days=1)
    log_data_str = log_date.isoformat()
    print log_data_str

    filtered = tlist.filter(u'@done = ' + log_data_str)
    filtered.remove_tag('done')
    entry_text = day_one_entry_title + \
        filtered.as_markdown(emphasise_done=False)

    full_text = u"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Creation Date</key>
    <date>{date}</date>
    <key>Entry Text</key>
    <string>{entry_text}</string>
    <key>Starred</key>
    <false/>
    <key>UUID</key>
    <string>{uid}</string>
</dict>
</plist>
""".format(
    uid=uid,
    entry_text=entry_text,
    date=log_date.strftime('%Y-%m-%dT23:59:59Z')
)
    with open(day_one_dir_path + uid + day_one_extension, 'w') as f:
        f.write(full_text.encode('utf-8'))


def update_daily(projects):
    daily = projects.filter('project = ' + daily_project_title)
    daily.remove_tag('done')


def update_weekly(onhold, inbox):
    today = days_of_the_week[date.today().weekday()]
    waiting = onhold.filter('@weekly = ' + today + ' +d')
    inbox.write('\n' + waiting.as_plain_text().encode('utf-8'))


def update_waiting(onhold, inbox):
    today = date.today().isoformat()
    waiting = onhold.filter('@waiting <= ' + today + ' +d', remove=remove_waiting_from_onhold)
    print waiting.as_plain_text()
    inbox.write('\n' + waiting.as_plain_text().encode('utf-8'))



all_lists = topy.from_files(topy.to_list())
inbox_file = open(inbox_path, 'a')
# archive_list = topy.from_file(archive_path)
onhold_list = topy.from_file(onhold_path)
print onhold_list.as_plain_text()
log_to_day_one(all_lists.deep_copy())
update_weekly(onhold_list, inbox_file)
update_waiting(onhold_list, inbox_file)
inbox_file.close()

update_daily(all_lists)
# archive(all_lists, archive_list)

# archive_list.to_file(archive_path)
topy.save(all_lists)
print 'done'
