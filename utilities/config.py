import os.path
import sys
sys.path += ['/path/to/topy']

###################### Paths ######################

inbox_path = 'path/to/Inbox.todo'
projects_path = 'path/to/Projects.todo'
onhold_path = 'path/to/Onhold.todo'
archive_path = 'path/to/NOTES/Archive.todo'

###################################################

#### print_today, print_deadlines, print_next #####

# path to files that contains variable if should print
# I use print_... scripts to put my todo list on
# desktop with Nerdtools and somtimes I want
# to hide it
should_print_path = 'path/to/should_print'

###################################################

###################### tvcal ######################

# http://www.pogdesign.co.uk/cat/
tvcal_url = ''  # link from .iCal
tvseries_project_title = 'TV Series:'

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
