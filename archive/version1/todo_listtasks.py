import sys
from config import only_tagged_today, today_tag, max_items_from_file, tasks_msg
from utils import is_not_done_task, format_line, create_arg
from alfredlist import AlfredItemsXML as AlfredList
import re


def list_file(path, query='', max_items=0, subtitle=tasks_msg):
    """
    Creates object that represents XML items list of tasks in file given by `path`
    that contains `query` as substring. Max length of list is given by `max_items`,
    0 means all tasks.
    """
    alist = AlfredList()

    if len(sys.argv) > 1:
        query = sys.argv[1].lower()

    items_added = 0
    with open(path, 'r') as f:
        for idx, line in enumerate(f):
            if is_not_done_task(line) and re.search(query, line.lower()):
                should_add = False
                if not only_tagged_today:
                    should_add = True
                else:
                    if today_tag in line:
                        should_add = True
                        line = line.replace(today_tag, '')
                        # when user displays only tasks with @today tag displaying it is reduntant
                if should_add:
                    items_added += 1
                    alist.append(create_arg(path, idx), format_line(line), subtitle)
                if max_items and max_items <= items_added:
                    break
    return alist


def list_files(paths, query='', max_items=max_items_from_file):
    """Creates listing of tasks from multiple files"""
    alist = AlfredList()
    for path in paths:
        subtitle = path.split('/')[-1]
        alist = alist + list_file(path, query, max_items, subtitle)
    return alist
