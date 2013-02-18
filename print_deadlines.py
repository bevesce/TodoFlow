from todolist_parser import Parser

t = Parser.from_file('/Users/bvsc/Dropbox/TODO/Projects.todo')
s = t.as_countdown(colored=True).split('\n')[0:5]
print '\n'.join(s)
