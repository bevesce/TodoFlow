#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path += ['/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/']

from todomd.config import tvcal_url, inbox_path, tvseries_project_title
from icalendar import Calendar
from urllib2 import urlopen
from datetime import datetime, timedelta
import re
now = datetime.now()
today = datetime(now.year, now.month, now.day)
tommorow = today + timedelta(hours=24)

inbox_text = open(inbox_path).read().decode('utf-8')

raw_cal = urlopen(tvcal_url).read()
cal = Calendar.from_ical(raw_cal)

season_x_episode_pattern = re.compile('(\d+)x(\d+)')


def s00e00(x00x00):
    return 's{0}e{1}'.format(
        x00x00.group(1).zfill(2),
        x00x00.group(2).zfill(2)
    )


def fix_summary(summary):
    splitted = summary.split(' - ')
    series_title = splitted[0]
    episode_title = splitted[1]
    if 'adventure time' in series_title.lower():
        series_title = re.sub(season_x_episode_pattern, '', series_title)
    else:
        series_title = re.sub(season_x_episode_pattern, s00e00, series_title)
        episode_title = ''

    return (series_title + episode_title).strip()


def tvcal(inbox_file):
    to_inbox = []
    for component in cal.walk():
        if 'summary' in component:
            summary = component['summary']
            dt = component['DTSTART'].dt
            fixed_summary = fix_summary(summary)
            if today <= dt <= tommorow and not fixed_summary in inbox_text:
                to_inbox.append(
                    '- ' + fixed_summary +
                    ' @at(' + str(dt) + ') @tvseries'
                )
    if len(to_inbox) > 0:
        inbox_file.write('\n' + '\n'.join(to_inbox) + '\n')

if __name__ == '__main__':
    with open(inbox_path, 'a') as inbox_file:
        tvcal(inbox_file)
