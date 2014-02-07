from .htmlprinter import HTMLPrinter

class HTMLLinkedPrinter(HTMLPrinter):
    def postprocess_item(self, item, text):
        if item.source:
            return u'<a href="file://{0}">{1}</a>'.format(item.source, text)
        else:
            return text