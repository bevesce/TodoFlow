import re
from cgi import escape
import config
from alfredlist import AlfredItemsList
from datetime import date
from filterpredicate import parse_predicate
import colors


class TodoList(object):
    items_by_id = {}
    _current_id = 0

    def __init__(self, items=None, set_new_parent=True):
        self.items = items if items else []
        if set_new_parent:
            for item in self.items:
                item.parent_list = self
        self.surce = None

    def to_file(self, path):
        with open(path, 'w') as f:
            f.write(self.as_plain_text(
                colored=False,
                with_ids=False,
                indent=True
                )
            )

    @classmethod
    def assign_id(cls, item):
        cls.items_by_id[cls._current_id] = item
        cls._current_id += 1
        return cls._current_id - 1

    # rocognizes words in parentheses ended
    # with white space or with eol
    tag_param_pattern = r"(\(([^(\s]*)\))(\s|\n|$)"

    @staticmethod
    def get_tag_param(text, tag):
        match = re.search(' @' + tag + TodoList.tag_param_pattern, text)
        if match:
            return match.group(2)
        return None

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
    def get_content(cls, id_no):
        return cls.items_by_id[id_no].title.content

    @classmethod
    def remove(cls, id_no):
        cls.items_by_id[id_no].remove_self_from_parent()

    def filter(self, predicate):
        # parse predicate if it's in string
        if isinstance(predicate, str):
            predicate = parse_predicate(predicate)

        filtered_items_with_None = [
            item.filter(predicate) for item in self.items
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
            if al_item:
                al += al_item
        return al

    def as_countdown(self, colored=False):
        today = date.today().isoformat()
        only_due = self.filter('(@due and not @done) or (@due >=' + today + ')')
        items_with_None = [item.as_countdown(colored) for item in only_due.items]
        items = [item for item in items_with_None if item]
        items.sort()
        return '\n'.join(items)

    def as_markdown(self, emphasise_done=True):
        return "\n".join(
            [item.as_markdown(emphasise_done) for item in self.items]
        )

    def as_html(self):
        items_html = "\n".join([item.as_html() for item in self.items])
        return "<ul>" + items_html + "</ul>"

    def as_full_html(self, css_style=None):
        return """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    {1}
</head>
<body>
<div class="whole">
    {0}
</div>
</body>""".format(
    self.as_html(),
    """<link href="{0}.css" rel="stylesheet" type="text/css" />""".format(css_style) if css_style else ''
    )

    def remove_item(self, item):
        self.items.remove(item)

    def add_parent(self, parent):
        for item in self.items:
            item.add_parent(parent)

    def find_project_id_by_title(self, title):
        """
        returns id of first project of given title in list
        returns None when there is no such item
        """
        filtered = self.filter('content = ' + title + ' and type ="project"')
        for item in filtered.items:
            if item.title.content == title:
                return item.title._id
            else:  # check sub tasks recursively
                if item.sub_tasks:
                    q = item.sub_tasks.find_project_id_by_title(title)
                    if q:
                        return q
        return None

    def remove_tag(self, tag):
        """removes every occurrence of given tag in list"""
        for item in self.items:
            item.remove_tag(tag)

    def __nonzero__(self):
        return bool(self.items)

    def __add__(self, other):
        new_list = TodoList(self.items + other.items)
        for item in new_list.items:
            item.parent_list = new_list
        return new_list

    def prepend(self, items_list):
        self.items = items_list + self.items

    def append(self, items_list):
        self.items += items_list

    def __str__(self):
        return "\n".join([str(s) for s in self.items])


class ItemTitle(object):
    def __init__(self, line, line_no, indent_level, typ):
        self.line = line
        self.text = extract_text(typ, line)
        self.content = extract_content(typ, line)
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

    def tag(self, tag_text, param=None):
        if self.line[-1] != ' ':
            self.line += ' '
        if self.text[-1] != ' ':
            self.text += ' '
        self.line += "@" + tag_text
        self.text += "@" + tag_text

        if param:
            self.line += '({0})'.format(param)
            self.text += '({0})'.format(param)

    def remove_tag(self, tag):
        self.text = remove_tag_from_text(self.text, tag)
        self.line = remove_tag_from_text(self.line, tag)
        self.content = remove_tag_from_text(self.content, tag)

    def is_done(self):
        return bool(re.search(' @done[\n\(\s )]', self.line))


class Item(object):
    def __init__(self, line='', line_no=None, indent_level=None, sub_tasks=None, typ='item'):
        self.title = ItemTitle(line, line_no, indent_level, typ)
        self.parent_item = None
        self.parent_list = None
        self.type = typ

        self.sub_tasks = sub_tasks
        TodoList.items_by_id[self.title._id] = self

        if self.sub_tasks:
            self.sub_tasks.add_parent(self)

    def markdown_indent_level(self):
        if self.type == 'project':
            return 0

        if self.parent_item:
            if self.parent_item.type == 'project':
                return 0
            return self.parent_item.markdown_indent_level() + 1
        else:
            return 0

    def filter(self, predicate):
        new = self.empty()
        new.title = self.title
        new.parent_item = self.parent_item
        new.parent_list = self.parent_list
        new.type = self.type
        if self.sub_tasks:
            new.sub_tasks = self.sub_tasks.filter(predicate)
        if predicate.test(self) or new.sub_tasks:
            return new

    def add_parent(self, parent):
        self.parent_item = parent

    def prepend_subtasks(self, items):
        if self.sub_tasks:
            self.sub_tasks = items + self.sub_tasks
        else:
            self.sub_tasks = items

    def append_subtasks(self, items):
        for item in items.items:
            item.title.indent_level = self.title.indent_level + 1
        if self.sub_tasks:
            self.sub_tasks = self.sub_tasks + items
        else:
            self.sub_tasks = items

    def tag(self, tag_text, param=None):
        self.title.tag(tag_text, param)

    def is_type(self, typ):
        return self.type == typ

    def is_done(self):
        return self.title.is_done()

    def remove_tag(self, tag):
        self.title.remove_tag(tag)
        if self.sub_tasks:
            self.sub_tasks.remove_tag(tag)

    def remove_self_from_parent(self):
        self.parent_list.remove_item(self)

    def as_plain_text(self, colored=False, with_ids=False, indent=True):
        actual_colors = get_actual_colors(self.title.colors, colored, self.is_done())
        ptext = "{indent}{ident_color}{ident}{prefix_color}{prefix}{text_color}{text}{postfix_color}{postfix}{def_color}{sub_tasks}".format(
            ident=(('- ' + str(self.title._id) + ' - ') if with_ids else ''),
            indent=(('\t' * self.title.indent_level) if indent else ''),
            text=modify_tags(self.title.text, actual_colors['tag_color'], actual_colors['text_color']),
            prefix=self.title.prefix,
            postfix=self.title.postfix,
            sub_tasks=(
                ('\n' + self.sub_tasks.as_plain_text(
                            colored, with_ids, indent)
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

    def parents_to_str(self):
        parents_contents = []
        item = self
        while item.parent_item:
            parents_contents.append(item.parent_item.title.content)
            item = item.parent_item
        return ' / '.join(parents_contents[::-1])

    def as_alfred_xml(self, include_projects=False, additional_arg=None):
        show_in_alfred = {
            'project': False,
            'note': True,
            'task': True,
        }
        a = AlfredItemsList()
        if self.type != 'project' or include_projects:
            a.append(
                arg=str(self.title._id) + ((';' + additional_arg) if additional_arg else ''),
                title=self.title.text,
                subtitle=self.parents_to_str(),
                )
        if self.sub_tasks:
            a += self.sub_tasks.as_alfred_xml(include_projects, additional_arg)
        return a

    def index(self):
        return str(self.parent_list.items.index(self))

    def as_countdown(self, colored=False):
        if not ' @due(' in self.title.text:
            return self.sub_tasks.as_countdown(colored)

        time_left = date_to_countdown(
            TodoList.get_tag_param(self.title.line, 'due')
            )

        actual_colors = get_actual_colors(
            self.title.colors, colored, self.is_done(), time_left[0] == '-')
        if time_left:
            ptext = "{time_left} {text_color}{text}{def_color}{sub_tasks}".format(
                time_left=time_left,
                text=modify_tags(self.title.text, actual_colors['tag_color'], actual_colors['countdown_text']),
                sub_tasks=(
                    ('\n' + self.sub_tasks.as_countdown(colored))
                    if self.sub_tasks else ''
                    ),
                text_color=actual_colors['countdown_text'],
                def_color=(colors.defc if colored else '')
                )
            return ptext
        else:
            return ''

    def as_markdown(self, *args):
        return ''

    def as_html(self):
        max_indent_level = 4
        indent_level = min(max_indent_level, self.title.indent_level)
        return '<li><span class="{type_class}{done_class}">{text}</span>{sub_tasks}</li>'.format(
            type_class=self.type + str(indent_level),
            done_class=(' done' if self.is_done() else ''),
            sub_tasks=(('\n' + self.sub_tasks.as_html()) if self.sub_tasks else ''),
            text=modify_tags(escape(self.title.text), '<span class="tag">', '</span>'),
            )

    def __str__(self):
        return "{indent}{prefix}{line}{postfix}{sub_tasks}".format(
            indent=('\t' * self.title.indent_level),
            line=self.title.text,
            prefix=self.prefix,
            postfix=self.postfix,
            sub_tasks=(
                ('\n' + self.sub_tasks.__str__()) if self.sub_tasks else ''
                )
            )


def date_to_countdown(date_iso):
    try:
        splitted = [int(x) for x in date_iso.split('-')]
        dat = date(splitted[0], splitted[1], splitted[2])
        td = date.today()
        countdown = str((dat - td).days)
        return countdown.zfill(3)
    except Exception as e:
        print e
        return '?' * 5

# date_to_countdown.longest_countdown = 0


class Project(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='project'):
        super(Project, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'project'

        self.title.colors['text_color'] = colors.blue

    def as_markdown(self, emphasise_done=True):
        indent = '#' * min(self.title.indent_level + 1, 5) + ' '
        text = modify_tags(self.title.text, '**', '**')
        if self.is_done() and emphasise_done:
            text = '*' + text + '*'
        title = '\n' + indent + text + '\n\n'
        sub_tasks = ''
        if self.sub_tasks:
            sub_tasks = self.sub_tasks.as_markdown()
        return title + sub_tasks

    def empty(self):
        return Project()


class Task(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='task'):
        super(Task, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.title.prefix = '- '
        self.type = 'task'

        self.title.colors['prefix_color'] = colors.blue
        self.title.colors['text_color'] = colors.defc

    def as_markdown(self, emphasise_done=True):
        indent_level = self.markdown_indent_level()
        indent = '\t' * indent_level + '- '
        text = modify_tags(self.title.text, '**', '**')
        if self.is_done() and emphasise_done:
            text = '*' + text + '*'
        title = indent + text
        sub_tasks = ''
        if self.sub_tasks:
            sub_tasks = '\n' + self.sub_tasks.as_markdown()
        return title + sub_tasks

    def empty(self):
        return Task()


class Note(Item):
    def __init__(self, line='', line_no=0, indent_level=0, sub_tasks=None, typ='note'):
        super(Note, self).__init__(line, line_no, indent_level, sub_tasks, typ)
        self.type = 'note'
        self.title.colors['text_color'] = colors.yellow

    def as_markdown(self, emphasise_done=True):
        indent = '\t' * max(self.title.indent_level, 1)
        text = modify_tags(self.title.text, '**', '**')
        title = '\n' + indent + text
        sub_tasks = ''
        if self.sub_tasks:
            sub_tasks = self.sub_tasks.as_markdown()
        return title + sub_tasks

    def empty(self):
        return Note()


class NewLineItem(object):
    def __init__(self):
        self.title = None

    def as_plain_text(self, *args):
        return ''

    def is_done(self, *args):
        return False

    def filter(self, *args):
        return False

    def as_alfred_xml(self, *args, **kwargs):
        return None

    def as_countdown(self, *args):
        return ''

    def as_markdown(self, *args):
        return '\n'

    def add_parent(self, parent):
        pass

    def as_html(self):
        return "<br>"


def get_actual_colors(def_colors, colored, is_done, is_overdue=False):
    res = {}
    for k in def_colors:
        if not colored:
            res[k] = ''
        elif is_done:
            res[k] = colors.gray
        else:
            res[k] = def_colors[k]
    res['countdown_text'] = colors.defc

    if is_done:
        res['countdown_text'] = colors.gray
        res['tag_color'] = colors.gray
    elif is_overdue:
        res['countdown_text'] = colors.red
        res['tag_color'] = colors.red
    if not colored:
        res['countdown_text'] = ''
        res['tag_color'] = ''
    return res


def remove_trailing_tags(line):
    splitted = line.split('@')
    if len(splitted) <= 1:
        return line
    idx = -1
    p = re.compile(r'[^\(\s]*(|\([^)]*\))')
    while p.match(splitted[idx]):
        if (len(splitted) + idx) == 1:
            break
        idx -= 1

    return '@'.join(splitted[0:idx]).strip()


def extract_content(typ, line):
    text = extract_text(line)
    if typ in ('task', 'note'):
        return remove_trailing_tags(text)
    elif typ == 'project':
        splitted = text.split(':')
        return ':'.join(splitted[0:-1])


def extract_text(typ, line):
    stripped = line.strip()
    if typ == 'task':
        return stripped[2:]
    return stripped


tag_pattern = re.compile(r' (@[^\(\s]*(\([^)]*\)|))')


def modify_tags(text, prefix, postfix):
    def f(t):
        return ' ' + prefix + t.group(1) + postfix
    return re.sub(tag_pattern, f, text)


def remove_tag_from_text(text, tag):
    tag_pattern = re.compile('@' + tag + '(\([^)]*\)|)')
    # text = text.replace('  ', ' ')
    return re.sub(tag_pattern, '', text)
