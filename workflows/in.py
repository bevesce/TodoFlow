import sys
import datetime as dt
from config import inbox_path

text = ' '.join(sys.argv[1:])
text = '- {} @in({})'.format(text, dt.date.today().isoformat())

with open(inbox_path, 'r') as f:
    if not f.read().endswith('\n'):
        text = '\n' + text

with open(inbox_path, 'a') as f:
    f.write(text)
