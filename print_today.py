from todolist_parser import Parser

t = Parser.from_file('/Users/bvsc/Dropbox/TODO/Projects.todo')
today_not_done = t.filter('@today and not @done')
today_not_done.remove_tag('today')
print today_not_done.as_plain_text(colored=True, indent=False)
# print ''
# due = t.filter('@due and not @done')
# print due.as_plain_text(colored=True, indent=False)
