#coding: utf-8

from cgi import escape
from todoflow.config import tag_to_class
from todoflow.src.utils import enclose_tags

template = u"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>todoflow</title>

    {1}

</head>

<body>

<ul>
{0}
</ul>

</body>
</html>
"""

class HTMLPrinter(object):
    def __init__(self, csspath='', included_css=False):
        self.csspath = csspath
        self.included_css = included_css

    def pprint(self, tlist):
        print(self.pformat(tlist))

    def pformat(self, tlist):
        result = []
        for item in tlist.items:
            result.append(self.pformat_item(item))
        joind = u'\n'.join(result)
        t = template.format(
            joind,
            self.cssify(),
        ).encode('utf-8')
        return t

    def pformat_item(self, item):
        title = self.titlize(item)
        sublist = [title]
        prefix = '<ul>'
        sufix = '</ul>'
        if item.type == 'seq-project':
            prefix = '<ol>'
            sufix = '</ol>'
        if item.sublist:
            sublist.append(prefix)
            for subitem in item.sublist.items:
                sublist.append(self.pformat_item(subitem))
            sublist.append(sufix + '</a>')
        text = '\n'.join(sublist)
        return self.postprocess_item(item, text)

    def postprocess_item(self, item, text):
        return text

    def titlize(self, item):
        text = self.preprocess_title(item)
        if item.type == 'project':
            return self.projecify(item, text)
        elif item.type == 'seq-project':
            return self.sprojecify(item, text)
        elif item.type == 'task':
            return self.taskify(item, text)
        elif item.type == 'newline':
            return self.newlineify(item, text)
        elif item.type == 'note':
            return self.noteify(item, text)
        return ''

    def preprocess_title(self, item):
        return enclose_tags(escape(item.text), '<span class="tag">', '</span>')

    def get_extra_classes(self, item):
        extra_classes = []
        for tag in tag_to_class:
            if item.has_tag(tag):
                extra_classes.append(tag_to_class[tag])
        return extra_classes

    def projecify(self, item, text):
        extra_classes = self.get_extra_classes(item)
        return u'<li class="project project-{lvl} {extra_classes}">{text}</li>'.format(
            text=text,
            lvl=item.indent_level + 1,
            extra_classes=' '.join(extra_classes)
        )

    def sprojecify(self, item, text):
        extra_classes = self.get_extra_classes(item)
        return u'<li class="project project-{lvl} {extra_classes}">{text}</li>'.format(
            text=text,
            lvl=item.indent_level + 1,
            extra_classes=' '.join(extra_classes)
        )

    def taskify(self, item, text):
        extra_classes = self.get_extra_classes(item)
        return u'<li class="task task-{lvl} {extra_classes}">{text}</li>'.format(
            text=text,
            lvl=item.indent_level + 1,
            extra_classes=' '.join(extra_classes)
        )

    def newlineify(self, item, text):
        return u'<li class="newline">&nbsp;</li>'

    def noteify(self, item, text):
        extra_classes = self.get_extra_classes(item)
        return u'<li class="note note-{lvl} {extra_classes}">{text}</li>'.format(
            text=text,
            lvl=item.indent_level + 1,
            extra_classes=' '.join(extra_classes)
        )

    def cssify(self):
        if self.included_css:
            return u'<style>{0}</style>'.format(self.included_css).encode('utf-8')
        elif self.csspath:
            return u'<style>{0}</style>'.format(open(self.csspath).read().encode('utf-8'))
        else:
            return u'<link rel="style.css" href="{0}" type="text/css" />'.format(self.csspath)
