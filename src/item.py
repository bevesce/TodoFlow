from .todolist import TodoList
from .title import ItemTitle

class Item(object):
    """
    Abstract item on todo list
    """
    def __init__(self, text='', indent_level=None, sublist=None, typ='item'):
        self.title = ItemTitle(text, indent_level, typ)
        self.parent_item = None
        self.parent_list = None
        self.type = typ
        self.sublist = sublist if sublist else TodoList()
        TodoList.items_by_id[self.title._id] = self

        self.sublist.add_parent(self)

        self._iter_returned_self = False
        self._iter_subtasks_idx = 0
        self.source = ''

    def __eq__(self, other):
        return self.title == other.title

    def __str__(self):
        return '\t' * self.indent_level + self.text

    def get_line(self):
        return self.title.text

    def copy(self):
        new = self.empty()
        new.title = self.title
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sublist = self.sublist.copy()
        new.type = self.type
        new.source = self.source
        return new

    def deep_copy(self):
        new = self.empty()
        new.title = self.title.deep_copy()
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sublist = self.sublist.deep_copy()
        new.type = self.type
        new.source = self.source
        return new

    def index(self):
        return self.parent_list.items.index(self)

    def indent(self, level=1):
        self.title.indent(level)
        self.sublist.indent(level)

    def tag_with_parents(self):
        self.tag('parents', self.parents_to_str())

    def remove_tag(self, tag):
        self.title.remove_tag(tag)
        self.sublist.remove_tag(tag)

    def is_nth_with_tag(self, number, tag):
        if not self.has_tag(tag) or self.has_tag('@done'):
            return False
        self_number = self.parent_list.tags_counters.get(tag, 0)
        self.parent_list.tags_counters[tag] = self_number + 1
        if number == self_number:
            return True
        else:
            return False

    def parents_to_str(self):
        parents_contents = []
        item = self
        while item.parent_item:
            parents_contents.append(item.parent_item.title.text)
            item = item.parent_item
        return ' / '.join(parents_contents[::-1])

    def set_source(self, path):
        self.source = path
        self.sublist.set_source(path)

    def add_parent(self, parent):
        self.parent_item = parent

    def remove_self_from_parent(self):
        self.parent_list.remove_item(self)

    def indent_new_subtasks(self, items):
        for item in items.items:
            item.title.set_indent_level(self.title.indent_level + 1)

    def set_indent_level(self, level):
        self.title.indent_level = level
        self.sublist.set_indent_level(level + 1)

    def prepend_subtasks(self, items):
        self.indent_new_subtasks(items)
        self.sublist = items + self.sublist

    def append_subtasks(self, items):
        self.indent_new_subtasks(items)
        self.sublist = self.sublist + items

    def is_type(self, typ):
        return self.type == typ

    def __getattr__(self, atr):
        return self.title.__getattribute__(atr)

    def filter(self, predicate):
        """
        Returns new item (with the same title object)
        if item itself or any of subtasks meets predicate.

        Subtasks of item are also filtered.

        If `remove` is set to True removes items that meet
        predicate from subtasks.
        """
        new = self.copy()
        new.sublist = self.sublist.filter(predicate)
        meets_prediacate = predicate.test(self)
        if meets_prediacate or new.sublist.items:
            return new


class Project(Item):
    def __init__(self, text='', indent_level = 0,sublist=None, typ='project'):
        text = text[:-1].strip()
        super(Project, self).__init__(text, indent_level, sublist, typ)
        self.type = typ

    def empty(self):
        return Project()

    def __str__(self):
        return (
            '\t' * self.indent_level + self.text + ':'
        )


import re

task_prefix = re.compile(r'^\s*- ')


class Task(Item):
    def __init__(self, text='', indent_level=0, sublist=None, typ='task'):
        text = task_prefix.sub('', text).strip()
        super(Task, self).__init__(text, indent_level, sublist, typ)
        self.type = typ

    def __str__(self):
        return (
            '\t' * self.indent_level + '- ' + self.text
        )

    def empty(self):
        return Task()


class Note(Item):
    def __init__(self, text='', indent_level=0, sublist=None, typ='note'):
        text = text.strip()
        super(Note, self).__init__(text, indent_level, sublist, typ)
        self.type = typ

    def empty(self):
        return Note()


class NewLineItem(Item):
    def __init__(self, text='', indent_level=0, sublist=None, typ='newline'):
        text = ''
        super(NewLineItem, self).__init__(text, indent_level, sublist, typ)

    def copy(self):
        return NewLineItem()

    def deep_copy(self):
        return NewLineItem()
