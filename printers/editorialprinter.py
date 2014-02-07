from .htmlprinter import HTMLPrinter

from todoflow.config import path_to_folder_synced_in_editorial

class EditorialPrinter(HTMLPrinter):
    def postprocess_item(self, item, text):
        if item.source:
            file_url = item.source.replace(path_to_folder_synced_in_editorial, '')
            return u'<a href="editorial://open/{0}?root=dropbox">{1}</a>'.format(file_url, text)
        else:
            return text