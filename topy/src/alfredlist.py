"""
Module provides simple class to create
Alfred 2 feedback XML.

It's really simple structure so there is no need
to use any advanced xml tools.
"""

from cgi import escape
from uuid import uuid1
from topy.config import white_symbols_on_icons


class AlfredItemsList(object):
    def __init__(self, items=None):
        self.items = items or []
        self.pattern = \
            '<item arg="{arg}" uid="{uid}" valid="{valid}">"' +\
            '<title>{title}</title>' +\
            '<subtitle>{subtitle}</subtitle>' +\
            '<icon>icons/{icon}{w}.png</icon>'.format(
                icon='{icon}',
                w='w' if white_symbols_on_icons else '',
            ) +\
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
        """
        Adds item to list, left uid of every item
        to None to preserve order in list when it's
        displayed in Alfred.
        """
        # using uuid is little hacky but there is no other way to
        # prevent alfred from reordering items than to ensure that
        # uid never repeats
        uid = uid or str(uuid1())
        self.items.append(
            (arg, escape(title), escape(subtitle), valid, icon, uid)
        )

    def __str__(self):
        items = "".join(
            [self.pattern.format(
                arg=arg,
                title=escape(title),
                subtitle=escape(subtitle),
                valid=valid,
                icon=icon,
                uid=uid
                ) for arg, title, subtitle, valid, icon, uid in self.items
            ]
        )
        return '<items>' + items + '</items>'

    def __add__(self, other):
        return AlfredItemsList(self.items + other.items)
