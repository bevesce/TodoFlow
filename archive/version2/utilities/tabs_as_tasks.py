import subprocess

command = 'cat /Users/bvsc/Dropbox/TODO/scripts/frontSafariTabs.applescript | osascript'
titles_and_urls_raw = subprocess.check_output(command, shell=True)
titles_and_urls = titles_and_urls_raw.split(', ')
task_template = '- {0} @web({1})'

for i in range(0, len(titles_and_urls), 2):
    print task_template.format(
        titles_and_urls[i].strip(),
        titles_and_urls[i + 1].strip()
    )
