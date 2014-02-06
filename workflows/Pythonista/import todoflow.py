import seamless_dropbox as sd
import os

path_to_todoflow_in_dropbox = 'Projects/todoflow'

dirs = [
    '/src',
    '/printers',
]

base = os.getcwd() + '/todoflow'

for dr in dirs:
    try:
        os.makedirs(base + dr)
    except OSError:
        pass 

files = [
    '/__init__.py',
    '/config.py',
    '/listfiles.py',
    '/printers/__init__.py',
    '/printers/colorprinter.py',
    '/printers/dayoneprinter.py',
    '/printers/editorialprinter.py',
    '/printers/htmllinkedprinter.py',
    '/printers/htmlprinter.py',
    '/printers/plainprinter.py',
    '/printers/pythonistaprinter.py',
    '/printers/utils.py',
    '/printers/xmlprinter.py',
    '/README.md',
    '/src/__init__.py',
    '/src/fileslist.py',
    '/src/item.py',
    '/src/lexer.py',
    '/src/main.py',
    '/src/parser.py',
    '/src/query.py',
    '/src/title.py',
    '/src/todolist.py',
    '/src/utils.py',
]


preambule = 'from seamless_dropbox import open\n\n'

for i, name in enumerate(files):
    print i + 1, '/', len(files), name
    t = sd.open(path_to_todoflow_in_dropbox + name).read()
    print(base + name)
    f = open(base + name, 'w')
    f.write(preambule + t)
    f.close()
print 'done'