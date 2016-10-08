"""
Compatiblity layer between python 2 and python 3 for some basic stuff
"""

try:
    unicode = unicode
    no_unicode = False
    def is_string(text):
        return isinstance(text, unicode) or isinstance(text, str)

except NameError:
    no_unicode = True
    unicode = str

    def is_string(text):
        return isinstance(text, str)
