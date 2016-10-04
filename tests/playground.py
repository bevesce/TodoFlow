import todoflow
from todoflow.parser import parse


t = parse("""Inbox:
\t- r
\t- e
""")


print(t)

