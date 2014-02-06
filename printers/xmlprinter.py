"""
Module provides simple class to create
Alfred 2 feedback XML.

It's really simple structure so there is no need
to use any advanced xml tools.
"""

from cgi import escape
from uuid import uuid1
from todoflow.config import white_symbols_on_icons

from plainprinter import PlainPrinter


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
                arg=arg.encode('utf-8'),
                title=escape(title.encode('utf-8')),
                subtitle=escape(subtitle.encode('utf-8')),
                valid=valid,
                icon=icon,
                uid=uid
                ) for arg, title, subtitle, valid, icon, uid in self.items
            ]
        )
        return '<items>' + items + '</items>'

    def __add__(self, other):
        return AlfredItemsList(self.items + other.items)


class XMLPrinter(PlainPrinter):
    def __init__(self):
        super(XMLPrinter, self).__init__()

    def pformat(self, tlist, *args):
        al = AlfredItemsList()
        additional_arg = ';'.join(args)
        for item in tlist:
            if item.type == 'project':
                self.seq_counter = [(0, 0)]
            elif item.type in ('task', 'note'):
                al.append(
                    arg=str(item._id) + (';' + additional_arg if additional_arg else ''),
                    title=self.titlize(item),
                    subtitle=item.parents_to_str(),
                    icon=self.iconize(item)
                )
            else:
                pass
        return str(al)

    def pprint(self, tlist, *args):
        print self.pformat(tlist, *args)

    def titlize(self, item):
        if item.type == 'note':
            return item.text
        elif item.type == 'task':
            return item.text

    def iconize(self, item):
        if item.type == 'note':
            return 'note'
        return 'task'
