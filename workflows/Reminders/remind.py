from datetime import datetime, timedelta, time, date
from create_reminder import create_reminder
from todomd.src.printers import PlainPrinter
import todomd


def set_reminders(todolist):
    for item in todolist.filter('@remind'):
        if item.has_tag('@remind'):
            remind_date_str = item.get_tag_param('@remind')
            try:
                remind_date = datetime.strptime(remind_date_str, '%Y-%m-%d %H:%M')
            except:
                try:
                    remind_date = datetime.strptime(remind_date_str, '%Y-%m-%d') + timedelta(hours=23, minutes=59)
                except:
                    remind_date = datetime.combine(date.today(), time(23, 59))
            item.remove_tag('remind')
            create_reminder(
                item.title.text,
                PlainPrinter().pformat(item.sublist),
                remind_date,
            )
            item.tag('willremind', param=remind_date_str)

if __name__ == '__main__':
    all_lists = todomd.from_files(todomd.lists.to_list())
    set_reminders(all_lists)
    todomd.save(all_lists)
