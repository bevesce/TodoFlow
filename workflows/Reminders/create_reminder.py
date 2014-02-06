import subprocess

applescript_template = u"""tell application \\"Reminders\\"
    set r to make new reminder
    set name of r to \\"{name}\\"
    set body of r to \\"{body}\\"
end tell"""

applescript_template_with_date = u"""tell application \\"Reminders\\"
    set r to make new reminder
    set name of r to \\"{name}\\"
    set body of r to \\"{body}\\"
    set remind me date of r to date \\"{reminde_me_date}\\"
end tell"""

applescript_template_with_list = u"""tell application \\"Reminders\\"
    set mylist to list \\"{list_name}\\"
    tell mylist
        set r to make new reminder
        set name of r to \\"{name}\\"
        set body of r to \\"{body}\\"
    end tell
end tell"""

applescript_template_with_list_and_date = u"""tell application \\"Reminders\\"
    set mylist to list \\"{list_name}\\"
    tell mylist
        set r to make new reminder
        set name of r to \\"{name}\\"
        set body of r to \\"{body}\\"
        set remind me date of r to date \\"{reminde_me_date}\\"
    end tell
end tell"""

def create_reminder(name, body, reminde_me_date=None, reminders_list=None, should_print=False):
    if reminde_me_date and not isinstance(reminde_me_date, str) and not  isinstance(reminde_me_date, unicode):
        reminde_me_date = reminde_me_date.strftime('%d-%m-%Y %H:%M')
            
    if reminders_list and reminde_me_date:
        applescript = applescript_template_with_list_and_date.format(
            name=name,
            body=body,
            reminde_me_date=reminde_me_date,
            list_name = reminders_list
        )
    elif reminde_me_date:
        applescript = applescript_template_with_date.format(
            name=name,
            body=body,
            reminde_me_date=reminde_me_date
        )
    elif reminders_list:
        applescript = applescript_template_with_list.format(
            name=name,
            body=body,
            list_name = reminders_list
        )
    else:
        applescript = applescript_template(
            name=name,
            body=body,
        )

    cmd = u'echo "{0}" | osascript'.format(applescript)
    if should_print:
        print cmd
    subprocess.check_output(
        cmd, shell=True
    )
