#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys

from config import inbox_path

reminders = json.loads(sys.argv[1].replace('\n', ' '))

res = []

for reminder in reminders:
    r = "- " + reminder["name"]
    if reminder["completed"]:
        r += " @done(" + reminder["completion_date"] + ')'
    if reminder["priority"] != "0":
        r += " @priority(" + reminder["priority"] + ")"
    if reminder["creation_date"] != "missing value":
        r += " @in(" + reminder["creation_date"] + ")"
    if reminder["due_date"] != "missing value":
        r += " @due(" + reminder["due_date"] + ")"
    if reminder["remind_me_date"] != "missing value":
        r += " @waiting(" + reminder["remind_me_date"] + ")"
    if reminder["body"] != "missing value":
        r += "\n\t" + "".join(reminder["body"].split('\n'))
    res.append(r)

f = open(inbox_path, 'a')
f.write("\n".join(res).encode('utf-8') + "\n")
f.close()
