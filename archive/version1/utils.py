import re


add_date_to_done_tag = True
done_tag = '@done'


def is_not_done_task(line):
    return re.match("^\s*-", line) and line.find(done_tag) == -1


def format_line(line):
    task_ind_idx = line.find('-')
    return line[task_ind_idx + 2:]  # skip '- '


def split_query(query):
    splitted = query.split(';')
    line_nr = int(splitted[0])
    path = ";".join(splitted[1:])
    return line_nr, path


def create_arg(path, idx):
    return '{0};{1}'.format(idx, path)
