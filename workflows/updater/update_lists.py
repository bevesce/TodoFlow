#!/usr/bin/python
from datetime import date, timedelta
import re
from todoflow import from_file
from todoflow.printers import PlainPrinter
from todoflow.config import days_of_the_week, projects_path, onhold_path, inbox_path, daily_project_title


def update_daily(projects):
    daily = projects.filter('project ? Daily')
    for item in daily:
        if item.type == 'task':
            item.remove_tag('done')
            item.tag('working')


def update_weekly(onhold, inbox):
    today = days_of_the_week[date.today().weekday()]
    waiting = onhold.filter('@weekly = ' + today + ' +d')
    inbox.write(PlainPrinter().pformat(waiting))


def update_waiting(onhold, inbox):
    today = date.today().isoformat()
    waiting = onhold.filter('@waiting <= ' + today + ' +d')
    inbox.write(PlainPrinter().pformat(waiting))


def update_followups(tasks):
    today = date.today()
    with open(onhold_path, 'a') as f:
        followups = tasks.filter('@followup and @done <= ' + date.today().isoformat())
        for item in followups:
            folowee = item.get_tag_param('@followup')
            if not folowee:
                continue
            days_no_str, folowee_task = folowee.partition(' ')[::2]
            days_no = int(days_no_str)
            when_to_follow = today + timedelta(days=days_no)
            following_param = item.title.get_text_without_tags()
            f.write(
                '- ' + folowee_task + ' @waiting(' + when_to_follow.isoformat() + ') @following(' + following_param + ')\n'
            )


def update_blocked(tasks):
    blockers = tasks.filter('@blocker and @done <= ' + date.today().isoformat())
    for blocker in blockers:
        if blocker.has_tag('@blocker'):
            blocker_id = blocker.get_tag_param('@blocker')
            blockeds = tasks.filter('@blocked = ' + blocker_id)
            for blocked in blockeds:
                if blocked.has_tag('@blocked'):
                    blocked.remove_tag_with_param('@blocked', blocker_id)


def update_incremental(tasks):
    incrementals = tasks.filter('@v')
    for task in incrementals:
        if task.has_tag('@v'):
            value_int = int(task.get_tag_param('@v'))
            inc = task.get_tag_param('@inc')
            if inc:
                inc_int = int(inc)
                new_value = value_int + inc_int
                task.replace_tag_param('v', str(new_value))

