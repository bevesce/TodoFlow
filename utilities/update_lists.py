#!/usr/bin/python
from datetime import date
from topy import from_file, archive
from config import days_of_the_week, projects_path, onhold_path, inbox_path, daily_project_title, remove_waiting_from_onhold

projects = from_file(projects_path)
onhold = from_file(onhold_path)

def update_daily(projects):
    daily = projects.filter('project = ' + daily_project_title)
    daily.remove_tag('done')


def update_weekly(onhold, inbox):
    today = days_of_the_week[date.today().weekday()]
    waiting = onhold.filter('@weekly = ' + today + ' +d')
    inbox.write('\n' + waiting.as_plain_text())


def update_waiting(onhold, inbox):
    today = date.today().isoformat()
    waiting = onhold.filter('@waiting <= ' + today + ' +d', remove=remove_waiting_from_onhold)
    inbox.write('\n' + waiting.as_plain_text())

if __name__ == '__main__':
    update_daily(projects)
    with open(inbox_path, 'a') as inbox:
        update_weekly(onhold, inbox)
        update_waiting(onhold, inbox)
        projects.to_file(projects_path)
