from .htmlprinter import HTMLPrinter

from todoflow.config import path_to_folder_synced_in_editorial

class EditorialPrinter(HTMLPrinter):
    def postprocess_item(self, item, text):
        if item.source:
            file_url = item.source.replace(path_to_folder_synced_in_editorial, '')
            return u'<a href="editorial://open/{0}?root=dropbox&command=goto&input={2}:{3}">{1}</a>'.format(
            	file_url, 
            	text, 
            	item.first_char_no,
            	item.first_char_no + \
            		len(item.text) + \
            		item.indent_level + \
            		(1 if item.type == 'task' else 0) + \
            		(-1 if item.type == 'note' else 0),
        	)
        else:
            return text