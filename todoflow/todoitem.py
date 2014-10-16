from .textutils import (
    is_task, is_project, is_note,
    calculate_indent_level, strip_formatting,
    add_tag, has_tag, get_tag_param, remove_tag,
)
from .config import (
    task_indicator, project_indicator,
    spaces_equal_to_tab
)


class Todoitem(object):
    _uniqueid_counter = 0

    @classmethod
    def from_text(cls, text):
        return Todoitem(text)

    @classmethod
    def _gen_uniqueid(cls):
        cls._uniqueid_counter += 1
        return unicode(cls._uniqueid_counter)

    def __init__(self, text):
        self.uniqueid = self._gen_uniqueid()
        self.text = strip_formatting(text) if text else ''
        self.indent_level = calculate_indent_level(text) if text else 0
        self._choose_text_formatter(text)

    def __unicode__(self):
        return self._text_formatter.format(self.text, self.indent_level)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _choose_text_formatter(self, text):
        if not text:
            self._text_formatter = EmptyLine()
        elif is_task(text):
            self._text_formatter = Task()
        elif is_project(text):
            self._text_formatter = Project()
        else:
            self._text_formatter = Note()

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

    def is_project(self):
        return self._text_formatter.is_project()

    def is_task(self):
        return self._text_formatter.is_task()

    def is_note(self):
        return self._text_formatter.is_note()

    def is_empty_line(self):
        return self._text_formatter.is_empty_line()

    def change_to_task(self):
        self._text_formatter = Task()

    def change_to_project(self):
        self._text_formatter = Project()

    def change_to_note(self):
        self._text_formatter = Note()


class AbstractTextFormatter(object):
    def _make_indentation(self, indent_level):
        return ' ' * indent_level

    def is_project(self):
        return False

    def is_task(self):
        return False

    def is_note(self):
        return False

    def is_empty_line(self):
        return False


class Task(AbstractTextFormatter):
    def format(self, text, indent_level):
        return ''.join([
            self._make_indentation(indent_level),
            task_indicator,
            text,
        ])

    def is_task(self):
        return True


class Note(AbstractTextFormatter):
    def format(self, text, indent_level):
        return self._make_indentation(indent_level) + text

    def is_note(self):
        return True


class Project(AbstractTextFormatter):
    def format(self, text, indent_level):
        return ''.join([
            self._make_indentation(indent_level),
            text,
            project_indicator
        ])

    def is_project(self):
        return True


class EmptyLine(AbstractTextFormatter):
    def format(self, text, indent_level):
        return ''

    def _class_repr(self, indent_level=0):
        return ' ' * indent_level + 'e'

    def is_empty_line(self):
        return True
