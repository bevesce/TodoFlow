import subprocess

applescript_template = u"""tell application \\"Reminders\\"
    set rs to reminders in list \\"{list_name}\\"
    repeat with r in rs
        delete r
    end repeat
end tell"""


def clear_reminders_list(list_name):
    applescript = applescript_template.format(
        list_name=list_name
    )
    cmd = u'echo "{0}" | osascript'.format(applescript)
    subprocess.check_output(
        cmd, shell=True
    )
