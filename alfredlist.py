from cgi import escape
from uuid import uuid1


class AlfredItemsList(object):
    def __init__(self, items=None):
        self.items = items or []
        self.pattern = \
            '<item arg="{0}" uid="{5}" valid="{3}">"' + \
            '<title>{1}</title>' + \
            '<subtitle>{2}</subtitle>' + \
            '<icon>{4}.png</icon>' + \
            '</item>'

    def append(
            self,
            arg,
            title,
            subtitle,
            valid='yes',
            icon='iconT',
            uid=None
        ):
        uid = uid or str(uuid1())  # use None it to preserve order of items
        self.items.append(
            (arg, escape(title), escape(subtitle), valid, icon, uid)
            )

    def __str__(self):
        items = "".join(
            [self.pattern.format(
                arg,
                escape(title),
                escape(subtitle),
                valid,
                icon,
                uid
                ) for arg, title, subtitle, valid, icon, uid in self.items]
            )
        return '<items>' + items + '</items>'

    def __add__(self, other):
        return AlfredItemsList(self.items + other.items)
