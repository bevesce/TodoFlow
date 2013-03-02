#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from datetime import date
from config import inbox_path

def inbox(msg):
    if msg[0] != ' ':
        msg = ' ' + msg
    if msg[-1] != ' ':
        msg += ' '
    to_write = "-" + msg + '@in(' + date.today().isoformat() + ')\n'
    with open(inbox_path, "a") as f:
        f.write(to_write)

inbox(sys.argv[1])
