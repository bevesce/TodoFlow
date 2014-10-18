from .textutils import (
    is_task, is_project, is_note,
    calculate_indent_level, strip_formatting,
    add_tag, has_tag, get_tag_param, remove_tag,
)
from .config import (
    task_indicator, project_indicator,
    spaces_equal_to_tab
)

from .printers import PlainPrinter


class Todoitem(object):
    _uniqueid_counter = 0

    @classmethod
    def from_text(cls, text):
        return Todoitem(text)

    @classmethod
    def _gen_uniqueid(cls):
        cls._uniqueid_counter += 1
        return unicode(cls._uniqueid_counter)

    def __init__(self, text=''):
        self.uniqueid = self._gen_uniqueid()
        self.text = strip_formatting(text) if text else ''
        self.indent_level = calculate_indent_level(text) if text else 0
        self._choose_type(text)

    def __unicode__(self):
        return PlainPrinter().handle_item(self, level=self.indent_level)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _choose_type(self, text):
        self._set_all_types_flags_to_false()
        if not text:
            self.is_empty_line = True
        elif is_task(text):
            self.is_task = True
        elif is_project(text):
            self.is_project = True
        else:
            self.is_note = True

    def _set_all_types_flags_to_false(self):
        self.is_task = False
        self.is_project = False
        self.is_note = False
        self.is_empty_line = False

    def tag(self, tag_to_use, param=None):
        self.text = add_tag(self.text, tag_to_use, param)

    def remove_tag(self, tag_to_remove):
        self.text = remove_tag(self.text, tag_to_remove)

    def has_tag(self, tag):
        return has_tag(self.text, tag)

    def get_tag_param(self, tag):
        return get_tag_param(self.text, tag)

    def edit(self, new_text):
        self.text = strip_formatting(new_text)

    def indent(self):
        self.indent_level += len(spaces_equal_to_tab)

    def dedent(self):
        self.indent_level = max(
            self.indent_level - len(spaces_equal_to_tab),
            0
        )

    def change_to_task(self):
        self._set_all_types_flags_to_false()
        self.is_task = True

    def change_to_project(self):
        self._set_all_types_flags_to_false()
        self.is_project = True

    def change_to_note(self):
        self._set_all_types_flags_to_false()
        self.is_note = True

    def change_to_empty_line(self):
        self._set_all_types_flags_to_false()
        self.is_empty_line = True
