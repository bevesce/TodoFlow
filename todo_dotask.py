from config import add_date_to_done_tag, done_tag
from datetime import date
from utils import split_query


def do_task(query):
    """
    decodes query from format used in listing and appends
    @done tag to the end of the line given by it's index
    """
    line_nr, path = split_query(query)

    with open(path, 'r') as f:
        lines = f.readlines()
    line = lines[line_nr][0:-1]
    line += " " + done_tag + \
        ('(' + date.today().isoformat() + ')' if add_date_to_done_tag else '') + \
        '\n'
    lines[line_nr] = line
    with open(path, 'w') as f:
        f.write("".join(lines))
