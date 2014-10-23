from __future__ import unicode_literals

import sys
import os
from cgi import escape
from uuid import uuid1

import todoflow as tf
import config
import utils

_template = """
<item arg="{arg}" uid="{uid}" valid="{valid}">"
<title>{title}</title>
<subtitle>{subtitle}</subtitle>
<icon>{icon}</icon>
</item>
""".strip().replace('\n', '')


class AlfredPrinter(tf.printers.AbstractPrinter):
    def unicode(self, todos_tree):
        todos_tree = self._eject_tree(todos_tree)
        return '<items>' + ''.join(self.convert_to_list(todos_tree)) + '</items>'

    def convert_task(self, item, node):
        return self.format_item(item, node, 'task')

    def convert_project(self, item, node):
        return self.format_item(item, node, 'project')

    def convert_note(self, item, node):
        return self.format_item(item, node, 'note')

    def format_item(self, item, node, type_name):
        return _template.format(
            arg=item.uniqueid,
            uid=str(uuid1()),
            valid='yes',
            title=escape(item.text),
            subtitle=escape(' / '.join([t.text for t in node.get_parents_values()])),
            icon=self.get_icon_path('done' if item.has_tag('done') else type_name)
        )

    def get_icon_path(self, type_name):
        base = utils.get_base_path()
        return os.path.join(base, 'img/' + type_name + '_icon.png')

    def make_indent(self, item, node):
        return ''

    def convert_empty_line(self, item, node):
        return None

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:])
    todos = tf.from_dir(config.tasks_dir_path)
    if query:
        todos /= query
    AlfredPrinter().pprint(todos)
