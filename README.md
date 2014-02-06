# todoflow 3

Todoflow is Python module that provides functions to parse, filter, update, modify and save todo lists stored in plain text files with TaskPaper syntax.

Using it I made several tools:

- CLI for searching
- GeekTool/NerdTool extension
- Alfred workflow
- Editorial.app search workflows
- Pythonista.app search
- lists updater
- Day One logger
- Reminders.app exporter & importer
- HTML exporter
- some other stuff...

Many workflows are probably too personal to use for anybody than me, but they can be adjusted and give example of what can be done.

# Changelog

- 2014-02-06 - **big changes** Ok, so this will be longer story. For several months I experimented with different syntax (something more like github flavored markdown, because I don't like that in TaskPaper it's not easy to distinguish done tasks without syntax highlighting), to do that I made major refactoring of the codebase. Now I decided that I want to come back to TaskPaper to be able to use other peoples tools. Instead of using old code I modified refactored one. Now code is cleaner (is it?), better organized (I think so), has some bugs fixed, but I dropped some parts that I was no longer using. I spread previously long readme through several folders, closer to code that it describe. Also I dropped attempts to change that horrible name - todoflow. Also Editorial workflow. I don't know if anybody is really using todoflow but if so beware.
- 2013-08-10 - added actions for @remind tag
- 2013-08-10 - added actions for @followup tag
- 2013-08-10 - added todify - iOS pythonista script that adds task tagged with *@today* to notification center
- 2013-05-19 - minor improvement in how abbreviations in queries are expanded
- 2013-05-14 - fixed bug in sublime package (bad changing type of item when project has trailing tags)
- 2013-05-11 - new utility - qr_to_drafts
- 2013-05-04 - new utility - tabs_as_tasks
- 2013-05-03 - added separate coloring for @today, @next and @due tags
- 2013-05-02 - Drafts Inbox actions added
- 2013-05-02 - added version for Pythonista iOS app
- 2013-05-02 - added editing from topy and Alfred workflow
- 2013-05-02 - better encoding handling
- 2013-05-02 - start of change log

# Installation

To install todoflow just download repository and put it somewhere on python path. After that read through and change config.py file. Probably most important is to set *files_list_path* and *files_list_name* variables. They point to file that should store path to every file with todo list that you want to be reachable from todoflow.

# Basics

Parsing lists:

    import todoflow
    todo_list = todoflow.all_lists()

Second line will creates object that represents all lists listed in file mentioned in *installation*. That list can be printed:

    # just as plain text:
    print todo_list 
    # or using one of the specific printers:
    from todoflow.printers import ColorPrinter
    ColorPrinter().pprint(todo_list) 

For each file new project is created, with title same as name of file.
To filter lists you can use:

    some_query = '@next and not @done'
    filtered_todo_list = todo_list.filter(some_query)

Filtering returns new todo list, object of the same class as original. Not only exact matches are part of this result, but whole projects structure (like in TaskPaper.app) - meaning that parents of matched item are also returned.

Parsed list can be iterated over and modified, for example we can add some tags:

    for task in todo_list:
        if task.type == 'task':
            task.add_tag('done')

and than save list to source file:

    todoflow.save(todo_list)

For more you'll need to read source code.

# Searching

Todoflow supports most of the query syntax of TaskPaper with few additions:

### syntax

Adds operator *?* that is synonym for *contains*.

### shortcuts

Shortcut are stored and configured in todoflow.config in *quick_query_abbreviations* dict. If every letter in first word of query is in this dict those letters will be expanded and joined with *quick_query_abbreviations_conjuction* (*and* is default).

For example with shortcuts defined as:

    quick_query_abbreviations = {
        't': '@today',
        'n': '@next',
        'd': 'not @done',
    }

Expanding will result in:

    >>> import todoflow as tf
    >>> tf.expand_shortcuts('dt')
    'not @done and @today'
    >>> tf.expand_shortucts('dt mac')
    'not @done and @today and mac'

If shortcuts conflict with some other query you can precede it with white space:

    >>> tf.expand_shortcuts(' dt mac')
    'dt mac'

### dates

Relative and natural*ish* language date and time expressions enclosed in *{}*.

Uses [parsedatetime](https://github.com/bear/parsedatetime), todoflow should not break when this module is not available to import, but it's cool so instal it.

    >>> tf.expand_dates('@due < {now + 7d}')
    '@due < 2014-02-13T13:22:07' # tags parameters are compared lexicographically

Both shortcuts and dates can be expanded using one function:

    >>> tf.expand_query('d @due < {next sunday}')
    'not @done and @due < 2014-02-09T14:07:08'

and both can be turned off in todoflow.config (*should_expand_dates* and *should_expand_shortcuts*)

# Project overview

- config.py - configuration file for todoflow and all workflows, you should remove parts you're not using
- printers - module with classes that can take todoflow todo list and return them as formatted string (*pformat*) or print them (*pprint*), modeled after pprint module
- src
    - main.py - functions to create and manage todo lists
    - todolist.py - class that represents parsed todo list
    - item.py - classes that represent single items on todo list, like task, project or note
    - query.py - parser, lexer and class of search queries
    - fileslist.py - module to manage list of files that contain todo lists
    - parser.py
    - lexer.py
    - utils.py
- workflows - all the stuff
- archive - previous major versions

# Workflows

Readmes for specific workflows are in their folders.




