#
# Configuration of todoflow
#

###################### Paths ######################
# File that stores path to your todo lists
files_list_path = '/Users/bvsc/Dropbox/Notes/__todo/'
files_list_name = 'lists'


inbox_path = '/Users/bvsc/Dropbox/Notes/__todo/_inbox.txt'
projects_path = '/Users/bvsc/Dropbox/Notes/__todo/Projects.taskpaper'
onhold_path = '/Users/bvsc/Dropbox/Notes/__todo/Onhold.taskpaper'
archive_path = '/Users/bvsc/Dropbox/Notes/__todo/NOTES/Archive.taskpaper'

##################### Queries #####################

should_expand_dates = True
should_expand_shortcuts = True

# logical operator to join shortened queries
quick_query_abbreviations_conjuction = ' and '  # ' or '

# fill with your own, this is what I use:
quick_query_abbreviations = {
    't': '@working',
    'n': '@next',
    'd': 'not @done',
    'u': '@due and not (project ? Onhold)',
    's': '@studia+d',
    'a': '((@working or @next) and not @done)+d',
}

# add date value when tagging with @done
date_after_done = True

# char that is before last ':' in project title that indicates that given project is sequential
# only first not @done task in sequential projects is returned in searches
sequential_projects_sufix = ':'

################## HTML printer ##################

# when generating html items are given classes
# define how many different classes (depengin on identation level)
# you want to have
number_of_css_classes = 4

path_to_css = '/Users/bvsc/Dropbox/Projects/todoflow/workflows/html/css/light.css'

tag_to_class = {
    'working': 'green',
    'next': 'blue',
    'due': 'orange',
    'done': 'done',
    'blocked': 'gray',
    'waiting': 'gray',
}

###################### Alfred ######################

# symbols on icons can be transparent or white
white_symbols_on_icons = False  # True

################## log to day one #################

logging_in_day_one_for_yesterday = True

# change if you store Day One entries somewhere else
day_one_dir_path = '/Users/bvsc/Dropbox/apps/day one/Journal.dayone/entries/'

# title of entry
day_one_entry_title = '# Things I did yesterday #\n\n\n'

day_one_extension = '.doentry'

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
daily_project_title = '"Daily:"'

###################### Inbox ######################

inbox_tag_to_path = {
    '@music': '/Users/bvsc/Dropbox/Notes/__todo/music.txt',
    '@film': '/Users/bvsc/Dropbox/Notes/__todo/filmy.txt',
    '@book': '/Users/bvsc/Dropbox/Notes/__todo/books.txt',
    '@app': '/Users/bvsc/Dropbox/Notes/__todo/apps.txt',
    '@game': '/Users/bvsc/Dropbox/Notes/__todo/games.txt',
    '@toy': '/Users/bvsc/Dropbox/Notes/__todo/toys and tools.txt',
    '@tool': '/Users/bvsc/Dropbox/Notes/__todo/toys and tools.txt',
    '@food': '/Users/bvsc/Dropbox/Notes/__todo/food and drinks.txt',
    '@idea': '/Users/bvsc/Dropbox/Notes/__todo/ideas.txt',
}

#################### Editorial ####################

path_to_folder_synced_in_editorial = '/Users/bvsc/Dropbox/Notes/'

###################### tvcal ######################

# http://www.pogdesign.co.uk/cat/
tvcal_url = 'http://www.pogdesign.co.uk/cat/generate_ics/bbec20975e1a472a3b76d4b0670fe733'
tvseries_project_title = 'TV Series:'

