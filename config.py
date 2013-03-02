#
# Configuration of topy
#
# You should read README first
#

# File that stores path to your todo lists
# This location keeps up with alfred workflow
# best practices but you can change it
# to wherever you want
files_list_path = '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/TodoFlow2/'
files_list_name = 'lists'

# logical operator to join shortened queries
quick_query_abbreviations_conjuction = ' and '  # ' or '

# fill with your own, this is what I use:
quick_query_abbreviations = {
    't': '@today',
    'n': '@next',
    'd': 'not @done',
    'u': '@due',
    's': 'project = Studia',
    'i': 'index = 0',
    'f': '(@today or @next)',
    'q': 'project = Projects and not project = Archive'
}

# add date value when tagging with @done
date_after_done = True

# include project titles in list displayed by alfred
# when searching with `q` keyword
include_project_title_in_alfred = False

# when generating html items are given classes
# define how many different classes (depengin on identation level)
# you want to have
number_of_css_classes = 4

# symbols on icons can be transparent or white
white_symbols_on_icons = False  # True
