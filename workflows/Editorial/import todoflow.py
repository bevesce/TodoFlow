path_to_folder_synced_in_editorial = '/Users/bvsc/Dropbox/Notes/'

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


preambule = """
import editor

path_to_folder_synced_in_editorial = '{0}'

def open(name, mode='r'):
    editorial_path = name.replace(path_to_folder_synced_in_editorial, '')
    content = editor.get_file_contents(editorial_path, 'dropbox')
    return FakeFile(content, editorial_path, mode)
    
class FakeFile(object):
    def __init__(self, content, name, mode):
        self.content = content
        self.name = name
        self.mode = mode
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass
        
    def read(self):
        return self.content
        
    def readlines(self):
        return [l + '\\n' for l in self.content.split('\\n')]

    def write(self, content):
        new_content = content
        if self.mode != 'a':
            new_content = self.content + '\\n' + new_content
        editor.set_file_contents (self.name, new_content, 'dropbox')

    def close(self):
        pass
            
""".format(path_to_folder_synced_in_editorial)
print(preambule)

for i, name in enumerate(files):
    print i + 1, '/', len(files), name
    t = sd.open(path_to_todoflow_in_dropbox + name).read()
    print(base + name)
    f = open(base + name, 'w')
    f.write(preambule + t)
    f.close()
print 'done'