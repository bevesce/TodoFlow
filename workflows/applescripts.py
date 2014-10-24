import subprocess


def run_applescript(script):
    cmd = u'echo "{0}" | osascript'.format(script.replace('"', '\\"'))
    subprocess.check_output(
        cmd, shell=True
    )


create_calendar_event_applescript = u"""tell application "Calendar"
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
        make new event at end with properties {{summary:"{title}", location:"{location}", start date:startDate, allday event:{all_day}, end date:endDate}}
    end tell
end tell
"""


def create_calendar_event(calendar, title, start_date, end_date=None, location='', all_day=True):
    if not end_date:
        end_date = start_date
    filled_applescript = create_calendar_event_applescript.format(
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
        all_day=str(all_day).lower(),
    )
    run_applescript(filled_applescript)


create_reminder_applescript = u"""tell application "Reminders"
    set r to make new reminder
    set name of r to "{title}"
    set body of r to "{note}"
    set remind me date of r to date "{remind_date}"
end tell"""


def create_reminder(title, remind_date, note=''):
    filled_applescript = create_reminder_applescript.format(
        title=title,
        remind_date=remind_date.strftime('%d-%m-%Y %H:%M'),
        note=note
    )
    run_applescript(filled_applescript)
