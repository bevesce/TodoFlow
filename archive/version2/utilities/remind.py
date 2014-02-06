from datetime import datetime
from create_reminder import create_reminder
import topy


def set_reminders(todolist):
    for item in todolist.filter('@remind +d'):
        if item.has_tag('@remind'):
            remind_date_str = item.get_tag_param('@remind')
            remind_date = datetime.strptime(remind_date_str, '%Y-%m-%d %H:%M')
            item.remove_tag('remind')
            create_reminder(
                item.title.text,
                item.sub_tasks.as_plain_text(indent=False) if item.sub_tasks else '',
                remind_date,
            )
            item.tag('willremind', param=remind_date_str)

if __name__ == '__main__':
    all_lists = topy.from_files(topy.lists.to_list())
    set_reminders(all_lists)
    topy.save(all_lists)
