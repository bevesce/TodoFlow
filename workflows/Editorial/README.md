2014-05-31: I successfully installed this workflows on iPhone, css styles are a little bit off because they have to big margins for smaller screen, I'll update this sometime after exams, maybe even using `ui` instead of html.

# Search Workflow

This is workflow that uses todoflow to filter todo lists inside Editorial.app.
When used it will display list of predefined queries in format:
    
    title | query

they can be set in workflow. Last position on list - *Query* is for single use queries (you'll be asked for input). 

Result will be displayed as html in in-app browser. Each item on list is also a link that will open source file in Editorial when activated. In workflows/html/css are several styles that can be used (paste them in workflow).


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
    - then install it using [this workflow](http://editorial-app.appspot.com/workflow/6442061712588800/hOafIlNIhTI), it asks for path (just *seamless_dropbox.py*) and creates file using content of clipboard
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
2. Install workflow from [here](http://editorial-app.appspot.com/workflow/5806813232496640/fWXVsgFK8x8)
3. And install this simple workflow from [here](http://editorial-app.appspot.com/workflow/5863197563158528/j4dZ5y1vnUk), it's used to select proper line when link in search results is activated

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

# Agenda

Requires todoflow. Shows Agenda view, similar to the one in CLI:

- *@due* tasks sorted by due date
- *@working* tasks
- *@next* tasks

You can install it from [here](http://editorial-app.appspot.com/workflow/5846893867302912/cI8nPxKUVr0)

# ✓ Toggle tags workflow

Requires todoflow. Toggles between *@next*, *@working* and *@done* tags.

You can install it from [here](http://editorial-app.appspot.com/workflow/5883366729580544/xx6KWCCP_Kg)

# ↱ Move to Project

Requires todoflow. Gets selected text, displays list of all projects and moves selection to chosen one - prepends new tasks.

You can install it from [here](http://editorial-app.appspot.com/workflow/5790251838603264/luMurs5X_zw)

Uses *Repeat* and *Save file contents* blocks to work around [this bug in editor.set_file_contents](http://omz-forums.appspot.com/editorial/post/5925732018552832).

![editorial query](http://procrastinationlog.net/img/editorialm2.png)
