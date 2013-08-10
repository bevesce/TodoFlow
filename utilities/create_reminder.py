import subprocess

applescript_template = """tell application \\"Reminders\\"
    set r to make new reminder
    set name of r to \\"{name}\\"
    set body of r to \\"{body}\\"
    set remind me date of r to date \\"{reminde_me_date}\\"
end tell"""


def create_reminder(name, body, reminde_me_date):
    reminde_me_date = reminde_me_date.strftime('%d-%m-%Y %H:%M')
    applescript = applescript_template.format(
        name=name,
        body=body,
        reminde_me_date=reminde_me_date,
    )
    cmd = 'echo "{0}" | osascript'.format(applescript)
    subprocess.check_output(
        cmd, shell=True
    )
