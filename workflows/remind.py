import todoflow
import applescripts
import todoflow.textutils as tu

path = '/Users/bvsc/Dropbox/Notes/tasks/Tasks.taskpaper'
todos = todoflow.from_path(path)
for item in todos.search('@remind'):
    param = item.get_tag_param('@remind')
    datetime = tu.parse_datetime(param)
    item.remove_tag('@remind')
    applescripts.create_reminder(item.text, datetime)
    print 'reminder:', item.text, datetime
    item.tag('@willremind', param=param)

todos.save(path)
