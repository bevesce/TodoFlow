"""
Compatiblity layer between python 2 and python 3 for some basic stuff
"""

try:
    unicode = unicode
    no_unicode = False
except NameError:
    no_unicode = True
    unicode = str
