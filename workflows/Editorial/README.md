# Editorial Workflow

This is workflow that uses todoflow to filter todo lists inside Editorial.app.
When used it will display list of predefined queries in format:
    
    title | query

they can be set in workflow. Last position on list - *Query* is for single use queries (you'll be asked for input). 

![editorial query](http://procrastinationlog.net/img/editorialquery.png)

Result will be displayed as html in in-app browser. Each item on list is also a link that will open source file in Editorial when activated. In workflows/html/css are several styles that can be used (paste them in workflow).

![editorial query](http://procrastinationlog.net/img/editorial2.png)

## Installation

### Excuses

Ok, installation is a little bit painful. There are few reasons for that:

1. I don't know any simple way to install multi-file python module in Editorial
2. I don't want to maintain several versions of todoflow (for Unix, for Editorial, for Pythonista...)
3. I didn't plan for that at the beginning

### Installing todoflow

You need to move whole files structure of todoflow to Editorial, probably there is better way but I do this like that:

1. Install and configure [seamless dropbox](https://github.com/bevesce/Seamless-Dropbox/blob/master/seamless_dropbox.py), you'll need app key and secret from [dropbox developer site](https://www.dropbox.com/developers/apps) (probably you should read what seamless dropbox does)
    - to do this you can download seamless dropbox from repo, configure it and put in clipboard
    - then install it using [this workflow](http://editorial-app.appspot.com/workflow/6099190178381824/FFr4Mx7Gg0U), it asks for path (just *seamless_dropbox.py*) and creates file using content of clipboard
2. Put configured todoflow in your dropbox
2. Paste content of *import todoflow.py* to Python scratchpad
3. Set variables *path_to_folder_synced_in_editorial* and *path_to_todoflow_in_dropbox* 
4. Run it

### Installing parsedatetime

1. Similar to todoflow, after installing seamless dropbox download parsedatetime to your dropbox
2. Paste content of *import parsedatetime.py* to Python scratchpad
3. Set variables *path_to_folder_synced_in_editorial* and *path_to_parsedatetime_in_dropbox* 
4. Run it

### Installing workflow

1. After installing todoflow and parsedatetime probably you'll need to restart app
2. Install workflow from [here](http://editorial-app.appspot.com/workflow/4953842659622912/-Kq8ZdSUGng)

### Installing todoflow in some other way

If you have better idea how to do this

1. Let me know
2. Read *import todoflow.py* before because there is some hacky stuff going on there

#### Hacky stuff

Obviously using *open* in Editorial won't work when using path from OSX, so before downloading every file with *import todoflow.py* I prepend it with this code:

    import editor

    def open(path, mode='r'):
        editorial_path = path.replace(path_to_folder_synced_in_editorial, '')
        content = editor.get_file_contents(editorial_path, 'dropbox')
        return FakeFile(content)
        
    class FakeFile(object):
        def __init__(self, content):
            self.content = content
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass
            
        def read(self):
            return self.content
            
        def readlines(self):
            return self.content.split('\\n')

it overwrites *open* from standard library with *open* that will work in Editorial (only for reading, at least for now).