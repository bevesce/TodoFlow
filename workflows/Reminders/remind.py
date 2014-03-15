from datetime import datetime, timedelta, time, date
from create_reminder import create_reminder
from todoflow.printers import PlainPrinter
import todoflow


def set_reminders(todolist):
    for item in todolist.filter('@remind'):
        if item.has_tag('@remind'):
            remind_date_str = item.get_tag_param('@remind')
            at = item.get_tag_param('at') if item.has_tag('at') else '23:59'
            date_str = remind_date_str + ' ' + at
            remind_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            item.remove_tag('remind')
            item.remove_tag('at')
            create_reminder(
                item.title.text,
                PlainPrinter().pformat(item.sublist),
                remind_date,
            )
            item.tag('willremind', param=date_str)
            print 'REMINDER:', item.title.text, remind_date

if __name__ == '__main__':
    t = todoflow.all_lists()
    set_reminders(t)
    todoflow.save(t)
