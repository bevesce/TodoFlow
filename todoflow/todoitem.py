from __future__ import absolute_import

from . import textutils as tu
from .compatibility import unicode


class Todoitem(object):
    """Representation of single todo item.

    It can be task, project or note.

    Note:
        `Todoitem` knows nothing about it's place in whole todos.
        `Todoitem` is mutable.
    """
    _id_counter = 1

    @classmethod
    def from_text(cls, text):
        return Todoitem(text)

    @classmethod
    def from_token(cls, token):
        item = Todoitem(token.text)
        item.line_number = token.line_number
        return item

    @classmethod
    def _gen_id(cls):
        cls._id_counter += 1
        return unicode(cls._id_counter)

    def __init__(self, text=''):
        """Creates `Todoitem` from text."""
        # internally text of todoitem is stored in stripped form
        # without '\t' indent,  task indicator - '- ',
        # and project indicator ':'
        self.id = self._gen_id()
        self.text = tu.strip_formatting(text) if text else ''
        self.type = tu.get_type(text or '')
        self.line_number = None

    def __unicode__(self):
        return self.get_text()

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return '<Todoitem: {} | "{}" | {}>'.format(
            self.id, self.text, self.type
        )

    def get_text(self):
        if self.type == 'task':
            return '- ' + self.text
        elif self.type == 'project':
            return self.text + ':'
        return self.text

    def get_id(self):
        return self.id

    def get_line_number(self):
        return self.line_number

    def get_tag_param(self, tag):
        return self.todoitem.get_tag_param(tag)

    def get_type(self):
        return self.type

    def tag(self, tag_to_use, param=None):
        self.text = tu.add_tag(self.text, tag_to_use, param)
        if self.is_project:
            self.text += " "

    def remove_tag(self, tag_to_remove):
        self.text = tu.remove_tag(self.text, tag_to_remove)

    def has_tag(self, tag):
        return tu.has_tag(self.text, tag)

    def get_tag_param(self, tag):
        return tu.get_tag_param(self.text, tag)

    def edit(self, new_text):
        self.text = tu.strip_formatting(new_text)

    def change_to_task(self):
        self.type = 'task'

    def change_to_project(self):
        self.type = 'project'

    def change_to_note(self):
        self.type = 'note'

    def change_to_new_line(self):
        self.type = 'newline'
