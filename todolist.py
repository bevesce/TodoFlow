import re
from alfredlist import AlfredItemsXML
from datetime import date
from filterpredicate import predicate as compile_predicate


class TodoList(object):
    items_by_id = {}
    current_id = 0

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
        cls.items_by_id[cls.current_id] = item
        cls.current_id += 1
        return cls.current_id - 1

    @staticmethod
    def get_tag_param(text, tag):
        match = re.search(' @' + tag + r"(\(([^\(\s]*)\)){0,1}(\s|$|\n)", text)
        if match:
            return match.group(2)
        return None

    @classmethod
    def tag(cls, id_no, tag, param=None):
        cls.items_by_id[id_no].tag(tag, param)

    @classmethod
    def do(cls, id_no):
        date_after_done = True
        cls.items_by_id[id_no].tag(
            'done',
            date.today().isoformat() if date_after_done else None
            )

    @classmethod
    def get_content(cls, id_no):
        return cls.items_by_id[id_no].title.content

    @classmethod
    def remove(cls, id_no):
        cls.items_by_id[id_no].remove_self_from_parent()

    def filter(self, predicate):
        if isinstance(predicate, str):
            predicate = compile_predicate(predicate)
        filtered_items = []
        for item in self.items:
            filtered_item = item.filter(predicate)
            if filtered_item:
                filtered_items.append(filtered_item)
        new_list = TodoList(filtered_items)
        return new_list

    def as_plain_text(self, colored=False, with_ids=False, indent=True):
        return "\n".join(item.as_plain_text(colored, with_ids, indent) for item in self.items)

    def as_alfred_xml(self, include_projects=False, additional_arg=None):
        al = AlfredItemsXML()
        for item in self.items:
            al_item = item.as_alfred_xml(include_projects, additional_arg)
            if al_item:
                al += al_item
        return al

    def as_countdown(self, colored=False):
        today = date.today().isoformat()
        only_due = self.filter('(@due and not @done) or (@due >=' + today + ')')
        items = [item.as_countdown(colored) for item in only_due.items if item.as_countdown()]
        items.sort()
        return '\n'.join([item for item in items if item])

    def as_markdown(self, done_emphasis=True):
        items_md = "\n".join([item.as_markdown(done_emphasis) for item in self.items])
        return items_md

    def as_html(self):
        items_html = "\n".join([item.as_html() for item in self.items])
        return "<ul>" + items_html + "</ul>"

    def as_full_html(self, css_style=None):
        return """<head>
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
        filtered = self.filter('content = ' + title + ' and type ="project"')
        for item in filtered.items:
            if item.title.content == title:
                return item.title._id
            else:
                if item.sub_tasks:
                    q = item.sub_tasks.find_project_id_by_title(title)
                    if q:
                        return q
        return None

    def remove_tag(self, tag):
        for item in self.items:
            item.remove_tag(tag)

    def remove_done_from_parents(self):
        for item in self.items:
            if item.is_done():
                print item.parent_list.as_plain_text()
                item.remove_self_from_parent()
                if item.sub_tasks:
                    item.sub_tasks.remove_done_from_parents(self)

    def archive(self):
        archive_id = self.find_project_id_by_title('Archive')
        if not archive_id:
            archive_project = Project(line='Archive:')
            archive_id = archive_project.title._id
            self.items.append(archive_project)
        self.remove_done_from_parents()
        done_tasks = self.filter("@done and not project = Archive")
        # done_tasks.add_parents_tag()
        TodoList.items_by_id[archive_id].prepend_subtasks(done_tasks)

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

import colors
from cgi import escape


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
        a = AlfredItemsXML()
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

    def as_markdown(self, done_emphasis=True):
        indent = '#' * min(self.title.indent_level + 1, 5) + ' '
        text = modify_tags(self.title.text, '**', '**')
        if self.is_done() and done_emphasis:
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

    def as_markdown(self, done_emphasis=True):
        indent_level = self.markdown_indent_level()
        indent = '\t' * indent_level + '- '
        text = modify_tags(self.title.text, '**', '**')
        if self.is_done() and done_emphasis:
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

    def as_markdown(self, done_emphasis=True):
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
    if typ == 'task':
        return remove_trailing_tags(line.strip()[2:])
    elif typ == 'note':
        return remove_trailing_tags(line.strip())
    elif typ == 'project':
        splitted = line.strip().split(':')
        return ':'.join(splitted[0:-1])


def extract_text(typ, line):
    if typ == 'task':
        return line.strip()[2:]
    else:
        return line.strip()

tag_pattern = re.compile(r' (@[^\(\s]*(\([^)]*\)|))')


def modify_tags(text, prefix, postfix):
    def f(t):
        return ' ' + prefix + t.group(1) + postfix
    return re.sub(tag_pattern, f, text)


def remove_tag_from_text(text, tag):
    tag_pattern = re.compile('@' + tag + '(\([^)]*\)|)')
    return re.sub(tag_pattern, '', text)
