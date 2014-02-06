from todoflow.printers.plainprinter import PlainPrinter
from datetime import date
from query import parse_predicate

done_tag = 'done'

class TodoList(object):
    items_by_id = {}
    _current_id = 0

    @classmethod
    def assign_id(cls, item):
        cls.items_by_id[cls._current_id] = item
        cls._current_id += 1
        return cls._current_id - 1

    @classmethod
    def tag(cls, id_no, tag, param=None):
        cls.items_by_id[id_no].tag(tag, param)

    @classmethod
    def do(cls, id_no):
        cls.items_by_id[id_no].tag(
            done_tag,
            date.today().isoformat()
        )

    @classmethod
    def get_item(cls, id_no):
        return cls.items_by_id[id_no]

    @classmethod
    def get_content(cls, id_no):
        return cls.items_by_id[id_no].get_content()

    @classmethod
    def get_text(cls, id_no):
        return cls.items_by_id[id_no].get_text()

    @classmethod
    def remove(cls, id_no):
        cls.items_by_id[id_no].remove_self_from_parent()

    @classmethod
    def edit(cls, id_no, new_content):
        cls.items_by_id[id_no].edit(new_content)

    def __init__(self, items=None):
        self.items = items if items else []
        self.set_parent_list(self.items)
        self.source = None
        self.tags_counters = {}
        self._iter_items_idx = 0
        self.type = 'list'

    def __iter__(self):
        for item in self.items:
            yield item
            for subitem in item.sublist:
                yield subitem

    def __add__(self, other):
        return TodoList(
            self.items + other.items
        )


    def __str__(self):
        return PlainPrinter().pformat(self)

    def copy(self):
        return TodoList(self.copy_of_items())

    def deep_copy(self):
        return TodoList(self.deep_copy_of_items())

    def copy_of_items(self):
        return [item.copy() for item in self.items if item]

    def deep_copy_of_items(self):
        return [item.deep_copy() for item in self.items]

    def remove_item(self, item):
        self.items.remove(item)

    def set_source(self, path):
        for item in self.items:
            item.set_source(path)

    def set_parent_list(self, items):
        for item in items:
            item.parent_list = self

    def add_parent(self, parent):
        for item in self.items:
            item.add_parent(parent)

    def indent(self, level=1):
        for item in self.items:
            item.indent(level)

    def dedent(self):
        self.indent(-1)

    def set_indent_level(self, level):
        for item in self.items:
            item.set_indent_level(level)

    def remove_tag(self, tag):
        """removes every occurrence of given tag in list"""
        for item in self.items:
            item.remove_tag(tag)

    def add_tag(self, tag, param=None):
        for item in self.items:
            item.tag(tag, param)

    def prepend(self, items_list):
        self.set_parent_list(items_list)
        self.items = items_list + self.items

    def append(self, items_list):
        self.set_parent_list(items_list)
        self.items += items_list

    def filter(self, predicate):
        """
        returns new list that contains only elements that
        meet predicate.

        Also if `remove` is set to True removes those elements
        from self.
        """
        # parse predicate if it's in string
        if isinstance(predicate, unicode) or isinstance(predicate, str):
            predicate = parse_predicate(predicate)

        filtered_items_with_None = [
            item.filter(predicate) for item in self.items
        ]
        filtered_items = [
            item for item in filtered_items_with_None if item
        ]
        new_list = TodoList(filtered_items)
        return new_list
