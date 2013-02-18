from cgi import escape


class AlfredItemsXML(object):
    def __init__(self):
        self.items = []
        self.pattern = '<item arg="{0}" uid="nouid" valid="{3}"><title>{1}</title><subtitle>{2}</subtitle><icon>iconT.png</icon></item>'

    def append(self, arg, title, subtitle, valid='yes'):
        self.items.append((arg, escape(title), escape(subtitle), valid))

    def __str__(self):
        items = "".join(
            [self.pattern.format(arg, escape(title), escape(subtitle), valid) for arg, title, subtitle, valid in self.items]
            )
        return '<items>' + items + '</items>'

    def __add__(self, other):
        new_alist = AlfredItemsXML()
        new_alist.items = self.items + other.items
        return new_alist
