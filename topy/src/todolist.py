# -*- coding: utf-8 -*-

"""
Module defines main objects of todolist structure:
- TodoList
- Item
- Task
- Project
- Note
- NewLineItem

"""

import re
from cgi import escape
import topy.config as config
from alfredlist import AlfredItemsList
from datetime import date
from filterpredicate import parse_predicate
from todolist_utils import *
import colors


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
            'done',
            date.today().isoformat() if config.date_after_done else None
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

    def __str__(self):
        return self.as_plain_text()

    def __nonzero__(self):
        return bool(self.items)

    def __add__(self, other):
        items = self.items

        first_trailing_newline_idx = len(items) - 1
        while first_trailing_newline_idx > 0 and\
              isinstance(items[first_trailing_newline_idx], NewLineItem):
            first_trailing_newline_idx -= 1
        first_trailing_newline_idx += 1

        items = \
            items[0:first_trailing_newline_idx] +\
            other.items + items[first_trailing_newline_idx:]

        return TodoList(
            items
            )

    def __iter__(self):
        return self

    def next(self):
        if not self.items:
            raise StopIteration
        try:
            return self.items[self._iter_items_idx].next()
        except StopIteration:
            self._iter_items_idx += 1
            if self._iter_items_idx >= len(self.items):
                raise StopIteration
            else:
                return self.items[self._iter_items_idx].next()

    def copy(self):
        return TodoList(self.copy_of_items())

    def deep_copy(self):
        return TodoList(self.deep_copy_of_items())

    def to_file(self, path):
        text = self.as_plain_text(
            colored=False,
            with_ids=False,
            indent=True
        ).code('utf-8')

        with open(path, 'w') as f:
            f.write(text)


    def copy_of_items(self):
        return [item.copy() for item in self.items if item]

    def deep_copy_of_items(self):
        return [item.deep_copy() for item in self.items]

    def remove_item(self, item):
        self.items.remove(item)

    def set_parent_list(self, items):
        for item in items:
            item.parent_list = self

    def add_parent(self, parent):
        for item in self.items:
            item.add_parent(parent)

    def indent(self, level=1):
        for item in self.items:
            item.indent(level)

    def set_indent_level(self, level):
        for item in self.items:
            item.set_indent_level(level)

    def remove_tag(self, tag):
        """removes every occurrence of given tag in list"""
        for item in self.items:
            item.remove_tag(tag)

    def tag_with_parents(self):
        """
        add tag `parents` with `/` separated list of parents
        to every item
        """
        for item in self.items():
            item.tag_with_parents()

    def flatten(self):
        """returns as flat list of items"""
        flattened = []
        for item in self.items:
            flattened += item.flatten()
        return flattened

    def prepend(self, items_list):
        self.set_parent_list(items_list)
        self.items = items_list + self.items

    def append(self, items_list):
        self.set_parent_list(items_list)
        self.items += items_list

    def find_project_id_by_title(self, title):
        """
        returns id of first project of given title in list
        returns None when there is no such item
        """
        filtered = self.filter('content = ' + title + ' and type ="project"')
        for item in filtered.items:
            if item.title.content == title:
                return item.title._id
            else:  # check subtasks recursively
                if item.sub_tasks:
                    q = item.sub_tasks.find_project_id_by_title(title)
                    if q:
                        return q
        return None

    def filter(self, predicate, remove=False):
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
            item.filter(predicate, remove) for item in self.items
        ]
        filtered_items = [
            item for item in filtered_items_with_None if item
        ]
        new_list = TodoList(filtered_items)
        return new_list

    def as_plain_text(self, colored=False, with_ids=False, indent=True):
        items_texts_list = [
            item.as_plain_text(colored, with_ids, indent) for item in self.items
        ]
        return "\n".join(items_texts_list)

    def as_alfred_xml(self, include_projects=False, additional_arg=None):
        al = AlfredItemsList()
        for item in self.items:
            al_item = item.as_alfred_xml(include_projects, additional_arg)
            if al_item:  # item returns None if it shouldn't be displayed in alfred
                al += al_item
        return al

    def as_countdown(self, colored=False):
        today = date.today().isoformat()
        only_due = self.filter(
            '((@due and not @done) or (@due >=' + today + ')) and not (@waiting > ' + today + ')'
        )
        items_with_None = [
            item.as_countdown(colored) for item in only_due.items
        ]
        items = [
            item for item in items_with_None if item
        ]
        items.sort()
        return '\n'.join(items)

    def as_markdown(self, emphasise_done=False):
        return "\n".join(
            [item.as_markdown(emphasise_done) for item in self.items]
        )

    def as_html(self):
        items_html = "\n".join([item.as_html() for item in self.items])
        return "<ul>" + items_html + "</ul>"

    def as_full_html(self, css_style=None):
        return u"""
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    {1}
</head>
<body>
<div class="container">
    {0}
</div>
</body>""".format(
    self.as_html(),
    u"""<link href="{0}" rel="stylesheet" type="text/css" />""".format(
        css_style
    ) if css_style else ''
)


class ItemTitle(object):
    def __init__(self, line, line_no, indent_level, typ):
        self.line = line
        self.text = extract_text(typ, line)
        self.content = extract_content(typ, line)
        self.type = typ
        # line, text & content at the moment
        # contain some redundant data

        self._id = TodoList.assign_id(self)
        self.line_no = line_no
        self.indent_level = indent_level

        self.prefix = ''
        self.postfix = ''

        self.colors = {}
        self.colors['ident_color'] = colors.defc
        self.colors['prefix_color'] = colors.defc
        self.colors['text_color'] = colors.defc
        self.colors['postfix_color'] = colors.defc
        self.colors['postfix_color'] = colors.defc
        self.colors['tag_color'] = colors.green

    def deep_copy(self):
        new = ItemTitle(
            line=self.line,
            line_no=0,
            indent_level=self.indent_level,
            typ=self.type
        )
        new.prefix = self.prefix
        new.postfix = self.postfix
        return new

    def set_indent_level(self, level):
        self.indent_level = level

    def remove_indent(self):
        self.indent_level = 0

    def edit(self, new_text):
        self.text = new_text.strip()
        self.content = remove_trailing_tags(self.text)

    def indent(self, level=1):
        self.indent_level += level

    def tag(self, tag_text, param=None):
        self.line = add_tag_to_text(self.line, tag_text, param)
        self.text = add_tag_to_text(self.text, tag_text, param)

    def remove_tag(self, tag):
        self.text = remove_tag_from_text(self.text, tag)
        self.line = remove_tag_from_text(self.line, tag)
        self.content = remove_tag_from_text(self.content, tag)

    def get_text_without_tags(self):
        return remove_tags(self.content)

    def has_tag(self, tag):
        return bool(re.search("(^| )" + tag + "($| |\()", self.text))

    def has_tags(self, tags):
        return all(self.has_tag(tag) for tag in tags)

    def has_any_tags(self, tags):
        return any(self.has_tag(tag) for tag in tags)

    def get_tag_param(self, tag):
        tag_search = '(^|(?<=\s))' + tag + r'\(([^)]*)\)'
        match = re.search(tag_search, self.text)
        if match:
            return match.group(2)

    def is_done(self):
        return bool(re.search(done_tag, self.line))


class Item(object):
    """
    Abstract item on todolist
    """
    def __init__(self, line='', line_no=None, indent_level=None, sub_tasks=None, typ='item'):
        self.title = ItemTitle(line, line_no, indent_level, typ)
        self.parent_item = None  # Project, Task or Note
        self.parent_list = None  # TodoList
        self.type = typ

        self.sub_tasks = sub_tasks
        TodoList.items_by_id[self.title._id] = self

        if self.sub_tasks:
            self.sub_tasks.add_parent(self)

        self._iter_returned_self = False
        self._iter_subtasks_idx = 0

    def __eq__(self, other):
        return self.title == other.title

    def __str__(self):
        return self.as_plain_text()

    def __iter__(self):
        return self

    def next(self):
        if not self._iter_returned_self:
            self._iter_returned_self = True
            return self
        if self._iter_returned_self and not self.sub_tasks:
            raise StopIteration
        else:
            return self.sub_tasks.next()


    def get_content(self):
        return self.title.content

    def get_text(self):
        return self.title.text

    def copy(self):
        new = self.empty()
        new.title = self.title
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sub_tasks = self.sub_tasks.copy() if self.sub_tasks else None
        new.type = self.type
        return new

    def deep_copy(self):
        new = self.empty()
        new.title = self.title.deep_copy()
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.sub_tasks = self.sub_tasks.deep_copy() if self.sub_tasks else None
        new.type = self.type
        return new

    def index(self):
        return self.parent_list.items.index(self)

    def remove_indent(self):
        self.title.remove_indent()

    def indent(self, level=1):
        self.title.indent(level)
        if self.sub_tasks:
            self.sub_tasks.indent(level)

    def tag(self, tag_text, param=None):
        self.title.tag(tag_text, param)

    def tag_with_parents(self):
        self.tag('parents', self.parents_to_str())

    def remove_tag(self, tag):
        self.title.remove_tag(tag)
        if self.sub_tasks:
            self.sub_tasks.remove_tag(tag)

    def has_tag(self, tag):
        return self.title.has_tag(tag)

    def has_tags(self, tags):
        return self.title.has_tags(tags)

    def has_any_tags(self, tags):
        return self.title.has_any_tags(tags)

    def is_nth_with_tag(self, number, tag):
        if not self.has_tag(tag) or self.has_tag('@done'):
            return False
        self_number = self.parent_list.tags_counters.get(tag, 0)
        self.parent_list.tags_counters[tag] = self_number + 1
        if number == self_number:
            return True
        else:
            return False

    def get_tag_param(self, tag):
        return self.title.get_tag_param(tag)

    def parents_to_str(self):
        parents_contents = []
        item = self
        while item.parent_item:
            parents_contents.append(item.parent_item.title.content)
            item = item.parent_item
        return ' / '.join(parents_contents[::-1])

    def add_parent(self, parent):
        self.parent_item = parent

    def remove_self_from_parent(self):
        self.parent_list.remove_item(self)

    def indent_new_subtasks(self, items):
        for item in items.items:
            item.title.set_indent_level(self.title.indent_level + 1)

    def set_indent_level(self, level):
        self.title.indent_level = level
        if self.sub_tasks:
            self.sub_tasks.set_indent_level(level + 1)

    def edit(self, new_content):
        self.title.edit(new_content)

    def prepend_subtasks(self, items):
        self.indent_new_subtasks(items)
        if self.sub_tasks:
            self.sub_tasks = items + self.sub_tasks
        else:
            self.sub_tasks = items

    def append_subtasks(self, items):
        self.indent_new_subtasks(items)
        if self.sub_tasks:
            self.sub_tasks = self.sub_tasks + items
        else:
            self.sub_tasks = items

    def flatten(self):
        self.tag_with_parents()
        flattened = []
        if self.type in ('note', 'task'):
            flattened.append(self.copy())
        if self.sub_tasks:
            flattened += self.sub_tasks.flatten()
        return flattened

    def is_type(self, typ):
        return self.type == typ

    def is_done(self):
        return self.title.is_done()

    def filter(self, predicate, remove=False):
        """
        Returns new item (with the same title object)
        if item itself or any of subtasks meets predicate.

        Subtasks of item are also filtered.

        If `remove` is set to True removes items that meet
        predicate from subtasks.
        """
        new = self.copy()
        if self.sub_tasks:
            new.sub_tasks = self.sub_tasks.filter(predicate, remove)
        meets_prediacate = predicate.test(self)
        if remove and new.sub_tasks:
            for item in new.sub_tasks.items:
                if predicate.test(item):
                    self.sub_tasks.items.remove(item)
        if meets_prediacate or new.sub_tasks:
            return new

    def as_plain_text(self, colored=False, with_ids=False, indent=True):
        actual_colors = get_actual_colors(
            self.title.colors,
            colored,
            self.is_done()
        )
        ptext = (u"{indent}{ident_color}{ident}"
                u"{prefix_color}{prefix}"
                u"{text_color}{text}"
                u"{postfix_color}{postfix}"
                u"{def_color}{sub_tasks}").format(
            ident=(
                (unicode(self.title._id) + ' | ') if with_ids else ''
            ),
            indent=(
                ('\t' * self.title.indent_level) if indent else ''
            ),
            text=wtf(self.title.text, actual_colors),
            prefix=self.title.prefix,
            postfix=self.title.postfix,
            sub_tasks=(
                ('\n' + self.sub_tasks.as_plain_text(
                    colored, with_ids, indent
                )
                )
                if self.sub_tasks else ''
            ),
            # colors
            ident_color=actual_colors['ident_color'],
            prefix_color=actual_colors['prefix_color'],
            text_color=actual_colors['text_color'],
            postfix_color=actual_colors['postfix_color'],
            def_color=(colors.defc if colored else '')
        )

        return ptext

    def as_alfred_xml(self, include_projects=False, additional_arg=None):
        al = AlfredItemsList()
        if self.type != 'project' or include_projects:
            al.append(
                arg=str(self.title._id) + \
                    ((';' + additional_arg) if additional_arg else ''),
                # _id never has `;` in it so it's safe encoding
                title=self.title.text,
                subtitle=self.parents_to_str(),
                icon='done' if self.is_done() else self.type
            )
        if self.sub_tasks:
            al += self.sub_tasks.as_alfred_xml(
                include_projects,
                additional_arg
            )
        return al

    def as_countdown(self, colored=False):
        if not ' @due(' in self.title.text:
            if self.sub_tasks:
                return self.sub_tasks.as_countdown(colored)

        time_left = date_to_countdown(
            get_tag_param(self.title.line, 'due')
        )

        actual_colors = get_actual_colors(
            self.title.colors,
            colored,
            self.is_done(),
            time_left[0] == '-'  # is ooverdue?
        )

        if time_left:
            text = u"{time_left} {text_color}{text}{def_color}{sub_tasks}".format(
                time_left=time_left,
                text=enclose_tags(
                    self.title.text,
                    prefix=actual_colors['tag_color'],
                    postfix=actual_colors['countdown_text']
                ),
                sub_tasks=(
                    ('\n' + self.sub_tasks.as_countdown(colored))
                        if self.sub_tasks else ''
                ),
                text_color=actual_colors['countdown_text'],
                def_color=(colors.defc if colored else '')
                )
            return text
        else:
            return ''

    def as_html(self):
        css_class_level = min(
            config.number_of_css_classes,
            self.title.indent_level
        )

        return u'<li><span class="{type_class}{done_class}">{text}</span>{sub_tasks}</li>'.format(
            type_class=self.type + str(css_class_level),
            done_class=(
                ' done' if self.is_done() else ''
            ),
            sub_tasks=(
                ('\n' + self.sub_tasks.as_html())
                    if self.sub_tasks else ''
            ),
            # text=unicode(self.title.text)
            text=enclose_tags(
                unicode(escape(self.title.text)),
                prefix=u'<span class="tag">',
                postfix=u'</span>'
            ),
        )

    def markdown_indent_level(self):
        if self.parent_item:
            if self.parent_item.type == 'project':
                return 0
            return self.parent_item.markdown_indent_level() + 1
        else:
            return 0

    def as_markdown(self, emphasise_done):
        indent = self.markdown_indent()
        text = enclose_tags(self.title.text, '**', '**')
        if self.is_done() and emphasise_done:
            text = '*' + text + '*'
        title = indent + text
        sub_tasks = ''
        if self.sub_tasks:
            sub_tasks = '\n' + self.sub_tasks.as_markdown()
        return title + sub_tasks


class Project(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='project'):
        super(Project, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'project'

        self.title.colors['text_color'] = colors.blue

    def markdown_indent_level(self):
        return 0

    def markdown_indent(self):
        return '\n' + '#' * min(self.title.indent_level + 1, 5) + ' '

    def empty(self):
        return Project()


class Task(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='task'):
        super(Task, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.title.prefix = '- '
        self.type = 'task'

        self.title.colors['prefix_color'] = colors.blue
        self.title.colors['text_color'] = colors.defc

    def markdown_indent(self):
        return '\t' * self.markdown_indent_level() + '- '

    def empty(self):
        return Task()


class Note(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='note'):
        super(Note, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'note'

        self.title.colors['text_color'] = colors.yellow

    def markdown_indent(self):
        return '\n' + '\t' * self.markdown_indent_level()

    def empty(self):
        return Note()


class NewLineItem(object):
    def __init__(self):
        self.title = None

    def __getattr__(self, name):
        """
        most functions of NewLineItem returns None and does
        nothing so they don't have to be implemented
        """
        def f(*args, **kwargs):
            pass
        return f

    def next(self):
        raise StopIteration

    def as_plain_text(self, *args):
        return ''

    def flatten(self, *args, **kwargs):
        return []

    def as_markdown(self, *args):
        return '\n'

    def copy(self):
        return NewLineItem()

    def deep_copy(self):
        return NewLineItem()

    def as_html(self):
        return "<br>"


def wtf(t, actual_colors):
    # try:
        # wtf = {
        #     u'ż': u'ż',
        #     u'ę': u'ę',
        #     u'ó': u'ó',
        #     u'ą': u'ą',
        #     u'ś': u'ś',
        #     u'ń': u'ń',
        #     u'ź': u'ź',
        #     u'ć': u'ć',
        #     u'ń': u'ń',
        # }
        # for k, v in wtf.items():
        #     t = t.replace(k, v)
        return u"{0}".format(enclose_tags(
            t,
            prefix=actual_colors['tag_color'],
            postfix=actual_colors['text_color']
        ))  #
    # except:
        # return 'WW'
