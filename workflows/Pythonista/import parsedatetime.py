path_to_folder_synced_in_editorial = '/Users/bvsc/Dropbox/Notes/'

import seamless_dropbox as sd
import os

path_to_parsedatetime_in_dropbox = 'Scripts/parsedatetime'

base = os.getcwd() + '/parsedatetime'

dirs = [
    '/parsedatetime',
]

for dr in dirs:
    try:
        os.makedirs(base + dr)
    except OSError:
        pass 

files = [
    '/__init__.py',
    '/parsedatetime.py',
    '/pdt_locales.py',
]

for i, name in enumerate(files):
    print i + 1, '/', len(files), name
    t = sd.open(path_to_parsedatetime_in_dropbox + name).read()
    print(base + name)
    f = open(base + name, 'w')
    f.write(preambule + t)
    f.close()
print 'done'
