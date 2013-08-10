#!/usr/bin/python
from datetime import date, timedelta
import re
from todolist_utils import remove_tags, get_tag_param
from topy import from_file, archive
from config import days_of_the_week, projects_path, onhold_path, inbox_path, daily_project_title, remove_waiting_from_onhold

projects = from_file(projects_path)
onhold = from_file(onhold_path)

def update_daily(projects):
    daily = projects.filter('project = ' + daily_project_title)
    daily.remove_tag('done')
    daily.add_tag('today')


def update_weekly(onhold, inbox):
    today = days_of_the_week[date.today().weekday()]
    waiting = onhold.filter('@weekly = ' + today + ' +d')
    inbox.write('\n' + waiting.as_plain_text().encode('utf-8') + '\n')


def update_waiting(onhold, inbox):
    today = date.today().isoformat()
    waiting = onhold.filter('@waiting <= ' + today + ' +d', remove=remove_waiting_from_onhold)
    inbox.write('\n' + waiting.as_plain_text().encode('utf-8') + '\n')



def update_followups(tasks):
    today = date.today()
    with open(onhold_path, 'a') as f:
        followups = tasks.filter('@followup and @done <= ' + date.today().isoformat())
        for line in followups.as_plain_text(indent=False, colored=False).split('\n'):
            folowee = get_tag_param(line, 'followup')
            if not folowee:
                continue
            days_no_str, folowee_task = folowee.partition(' ')[::2]
            days_no = int(days_no_str)
            when_to_follow = today + timedelta(days=days_no)
            following_param = remove_tags(line).strip()
            if following_param.startswith('- '):
                following_param = following_param[2:]
            f.write(
                '- ' + folowee_task + ' @waiting(' + when_to_follow.isoformat() + ') @following(' + following_param + ')\n'
            )


if __name__ == '__main__':
    update_daily(projects)
    with open(inbox_path, 'a') as inbox:
        update_weekly(onhold, inbox)
        update_waiting(onhold, inbox)
        projects.to_file(projects_path)
