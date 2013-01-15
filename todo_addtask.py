import re
from config import inbox


def prepend(path, task):
    with open(path, 'r') as f:
        lines = f.readlines()
        lines.insert(0, '- ' + task + '\n')
    with open(path, 'w') as f:
        f.write("".join(lines))


def append(path, task):
    with open(path, 'a') as f:
        f.write('\n- ' + task)


def insert_into_inbox(path, task):
    """
    Inserts task in the next line to line containing 'Inbox:'
    Task is indented by one more tab than Inbox.
    """
    with open(path, 'r') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if re.match('\s*' + inbox + ':', line):
                tabs_no = line.find(inbox[0])
                lines.insert(idx + 1, '\t' * tabs_no + '\t- ' + task + '\n')
                break
    with open(path, 'w') as f:
        f.write("".join(lines))
