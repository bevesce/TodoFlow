from utils import enclose_tags

class PlainPrinter(object):
    def __init__(self, indent_char='\t'):
        # self.seq_counter = [(0, 0)]
        self.indent_char = indent_char
        self.prev_tag = ''
        self.post_tag = ''

    def pformat(self, tlist):
        result = []
        for item in tlist:
            if item.type == 'project':
                result.append(self.project(item))
            elif item.type == 'task':
                result.append(self.task(item))
            elif item.type == 'note':
                result.append(self.note(item))
            else:
                result.append('')
        return '\n'.join(result).encode('utf-8').strip() + '\n'

    def pprint(self, tlist):
        print self.pformat(tlist)

    def project(self, item):
        return self.indent_char * item.indent_level + enclose_tags(item.text, self.prev_tag, self.post_tag) + ':'

    def task(self, item):
        return self.indent_char * item.indent_level + '- ' + enclose_tags(item.text, self.prev_tag, self.post_tag)

    def note(self, item):
        return self.indent_char * item.indent_level + enclose_tags(item.text, self.prev_tag, self.post_tag)
