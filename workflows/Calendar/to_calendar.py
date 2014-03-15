import todoflow
from todoflow.src.utils import remove_tag
import subprocess
from datetime import datetime

applescript = """tell application "Calendar"
	tell calendar "{calendar}"
		set startDate to current date
		set the year of startDate to {start_year}
		set the month of startDate to {start_month}
		set the day of startDate to {start_day}
		set the hours of startDate to {start_hour}
		set the minutes of startDate to {start_minute}
		set endDate to current date
		set the year of endDate to {end_year}
		set the month of endDate to {end_month}
		set the day of endDate to {end_day}
		set the hours of endDate to {end_hour}
		set the minutes of endDate to {end_minute}
		make new event at end with properties {{summary:"{title}", location:"{location}", start date:startDate, allday event:{allday}, end date:endDate}}
	end tell
end tell
"""

tag_to_calendar = {
	'date': 'Kalendarz',
	'due': 'Deadlines',
}

def create_event(calendar, title, start_date, location='', end_date=None, allday=False):
	if not end_date:
		end_date = start_date
	filled_applescript = applescript.format(
		calendar=calendar,
		title=title,
		location=location,
		start_year=start_date.year,
		start_month=start_date.month,
		start_day=start_date.day,
		start_hour=start_date.hour,
		start_minute=start_date.minute,
		end_year=end_date.year,
		end_month=end_date.month,
		end_day=end_date.day,
		end_hour=end_date.hour,
		end_minute=end_date.minute,
		allday=str(allday).lower(),
	)
	print filled_applescript
	print ''
	cmd = u'echo "{0}" | osascript'.format(filled_applescript.replace('"', '\\"'))
	subprocess.check_output(
	    cmd, shell=True
	)

def parse_dates(task, date_str):
	year, month, day = date_str.split('-')
	year = int(year)
	month = int(month)
	day = int(day)
	start_hour = 0
	end_hour = 0
	start_minute = 0
	end_minute = 0
	allday = True
	if task.has_tag('at'):
		allday = False
		at = task.get_tag_param('at').split('-')
		start_hour, start_minute = at[0].split(':')
		start_hour = int(start_hour)
		start_minute = int(start_minute)
		if len(at) == 2:
			end_hour, end_minute = at[1].split(':')
			end_hour = int(start_hour)
			end_minute = int(start_minute)
		else:
			end_minute = start_minute
			end_hour = start_hour + 1
			if (end_hour > 23):
				end_hour = 23
				end_minute = 59
	start_date = datetime(year, month, day, start_hour, start_minute)
	end_date = datetime(year, month, day, end_hour, end_minute)
	return start_date, end_date, allday


def get_title(task):
	title = task.text
	for tag in ['due', 'date', 'at', 'place']:
		title = remove_tag(title, tag)
	title = title.strip()
	return title

# @due/@date - start date day
# @at(15:00) - start date time
# @at(15:00-16:00) - start date time - end date time
# @place - location
# not @at - allday = true

def create_event_for_task(task):
	calendar = ''
	date_str = ''
	for tag, calendar_for_tag in tag_to_calendar.items():
		if task.has_tag(tag):
			calendar = calendar_for_tag
			date_str = task.get_tag_param(tag)
	location = ''
	if task.has_tag('place'):
		location = task.get_tag_param('place')
	start_date, end_date, allday = parse_dates(task, date_str)
	title = get_title(task)
	print 'CALENDAR:', title, location, 'allday =', allday, start_date, end_date
	create_event(
		calendar=calendar,
		title=title,
		allday=allday,
		start_date=start_date,
		end_date=end_date,
		location=location
	)
	task.tag('calendar')


def create_events_for_list(t):
	for item in t.filter('(@due or @date) and not @calendar'):
		if (item.has_tag('@due') or item.has_tag('@date')) and not item.has_tag('calendar'):
			create_event_for_task(item)


if __name__ == '__main__':
	t = todoflow.all_lists()
	create_events_for_list(t)
	todoflow.save(t)