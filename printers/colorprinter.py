from .utils import enclose_tags
from todoflow.config import sequential_projects_sufix

class color:
    """defines colors used in output"""
    defc         = '\033[0m'

    red          = '\033[1;31m'
    green        = '\033[1;32m'
    gray         = '\033[1;30m'
    blue         = '\033[1;34m'

    yellow       = '\033[1;33m'
    magenta      = '\033[1;35m'
    cyan         = '\033[1;36m'
    white        = '\033[1;37m'
    crimson      = '\033[1;38m'

    high_red     = '\033[1;41m'
    high_green   = '\033[1;42m'
    high_brown   = '\033[1;43m'
    high_blue    = '\033[1;44m'
    high_magenta = '\033[1;45m'
    high_cyan    = '\033[1;46m'
    high_gray    = '\033[1;47m'
    high_crimson = '\033[1;48m'


class ColorPrinter(object):
    def __init__(self):
        self.seq_counter = [(0, 0)]
        self.prev_tag = color.green
        self.post_tag = color.defc

    def pformat(self, tlist):
        result = []
        for item in tlist:
            if item.type == 'project':
                result.append(color.blue + self.project(item) + color.defc)
            elif item.type == 'seq-project':
                result.append(color.magenta + self.sproject(item) + color.defc)
            elif item.type == 'task':
                result.append(self.task(item))
            elif item.type == 'note':
                result.append(self.note(item))
            elif item.type == 'newline':
                result.append('')
        return '\n'.join(result).encode('utf-8').strip() + '\n'

    def pprint(self, tlist):
        print(self.pformat(tlist))

    def project(self, item):
        return '\t' * item.indent_level + enclose_tags(item.text, self.prev_tag, self.post_tag) + ':'

    def sproject(self, item):
        return '\t' * item.indent_level + enclose_tags(item.text, self.prev_tag, self.post_tag) + sequential_projects_sufix + ':'

    def task(self, item):
        return '\t' * item.indent_level + color.blue + '- ' + color.defc + enclose_tags(item.text, self.prev_tag, self.post_tag)

    def note(self, item):
        return color.yellow + '\t' * item.indent_level + enclose_tags(item.text, self.prev_tag, self.post_tag) + color.defc
