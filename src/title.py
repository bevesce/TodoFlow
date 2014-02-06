from utils import create_tag_pattern, remove_tags, fix_tag
from todolist import TodoList

tag_prefix = '@'

class ItemTitle(object):
    def __init__(self, text, indent_level, typ):
        self.text = text.rstrip()
        self._id = TodoList.assign_id(self)
        self.indent_level = indent_level
        self.type = typ
        self.prefix = ''
        self.postfix = ''

    def deep_copy(self):
        new = ItemTitle(
            text=self.text,
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

    def edit(self, new_line):
        self.text = new_line

    def indent(self, level=1):
        self.indent_level += level

    def tag(self, tag_text, param=''):
        self.remove_tag(tag_text)
        if param:
            param = '(' + param + ')'
        else:
            param = ''

        tag_text = tag_text.strip()
        if not tag_text.startswith(tag_prefix):
            tag_text = tag_prefix + tag_text
        if self.type == 'project':
            self.text = self.text.rstrip()[0:-1] + ' ' + tag_text + param + ':'
        else:
            self.text = self.text.rstrip() + ' ' + tag_text + param
        return self.text

    def remove_tag(self, tag):
        p, _ = create_tag_pattern(tag)
        self.text = p.sub('', self.text)

    def remove_tag_with_param(self, tag, param):
        tag = fix_tag(tag)
        self.text = self.text.replace(tag + '(' + param + ')', '')
        self.text = self.text.replace(tag + '[' + param + ']', '')
        self.text = self.text.replace(tag + '{' + param + '}', '')

    def get_text_without_tags(self):
        return remove_tags(self.text)

    def get_text(self):
        return self.text

    def has_tag(self, tag):
        p, _ = create_tag_pattern(tag)
        return bool(p.search(self.text))

    def has_tags(self, tags):
        return all(self.has_tag(tag) for tag in tags)

    def has_any_tags(self, tags):
        return any(self.has_tag(tag) for tag in tags)

    def get_tag_param(self, tag):
        p, param_group = create_tag_pattern(tag)
        match = p.search(self.text)
        if match:
            return match.group(param_group)[1:-1]

    def replace_tag_param(self, tag, new_param):
        p, _ = create_tag_pattern(tag)
        tag = fix_tag(tag)
        self.text = p.sub(' ' + tag + '(' + new_param + ')', self.text)

    def is_done(self):
        return self.has_tag(tag_prefix + 'done')

