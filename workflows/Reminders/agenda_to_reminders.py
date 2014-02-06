import sys
sys.path.append('/Users/bvsc/Dropbox/Projects')
import todoflow

from datetime import datetime, date

from clear_reminders_list import clear_reminders_list
from create_reminder import create_reminder


def clear_lists():
    print 'clearing'
    to_clear = ['Working', 'Next', 'Deadlines', 'Contexts', 'Inbox']
    for l in to_clear:
        clear_reminders_list(l)
    print 'cleared'


def export_deadlines(t):
    due = t.filter('@due and not @done and not project $ onhold')
    for item in due:
        if item.has_tag('due'):
            param = item.get_tag_param('due')
            due_date = datetime.strptime(param, '%Y-%m-%d')
            if item.has_tag('at'):
                hour_str, minutes_str = item.get_tag_param('at').split(':')
                due_date = due_date.replace(hour=int(hour_str), minute=int(minutes_str))
            else:
                due_date = due_date.replace(hour=23, minute=59)
            create_reminder(item.text, item.parents_to_str(), due_date, 'Deadlines', should_print=True) 


def export_today(t):
    items = t.filter('@working and not @done')
    for item in items:
            if item.has_tag('@working'):
                due_date = datetime.now()
                if item.has_tag('at'):
                    hour_str, minutes_str = item.get_tag_param('at').split(':')
                    due_date = due_date.replace(hour=int(hour_str), minute=int(minutes_str))
                else:
                    due_date = due_date.replace(hour=23, minute=59)
                create_reminder(item.text, item.parents_to_str(), due_date, 'Working', should_print=True)


def export_generic(t, query, tag, list_name):
    items = t.filter(query)
    for item in items:
        if tag:
            if item.has_tag(tag):
                create_reminder(item.text, item.parents_to_str(), reminders_list=list_name, should_print=True)



def export_contexts(t):
    items = t.filter('project $ Contexts')
    for item in items:
        if item.text.startswith('@ ') or item.text == '':
            continue
        create_reminder(item.text, item.parents_to_str(), reminders_list='Contexts', should_print=True)



def export():
    clear_lists()
    t = todoflow.from_files(todoflow.lists.to_list())
    export_deadlines(t)
    export_today(t)
    export_generic(t, '@next and not @done and not @today', '@next', 'Next')
    export_contexts(t)


if __name__ == '__main__':
    export()
    print 'done'