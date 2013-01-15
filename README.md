# TodoFlow

[Alfred][] 2 (beta) workflow for interacting with plain text todo lists with [TaskPaper][] syntax.

## Basic usage


### Keyword: *t*

Set path to your master todo list in config.py (one_filepath). When you type **t** keyword Alfred will display all tags from that list.

![All tasks][basic]

Typing query filters tasks. You can use it to show only tasks with given tag.

![Querying tasks][query]

It works with regular expressions too! (I'm not sure if it useful in any way).

![Querying tasks with regexp][regexp]

Pressing *return* tags task as done.
Adding date value after tag can be configured.
Pressing *cmd+return* opens file containing task.

You can also add task to that list. There are 3 options: prepend, append and insert into Inbox project. That can be configured inside workflow in third script from the top.

## Advanced usage

Work with multiple files.

### Keyword: *tt*

Lists tasks from multiple lists.
Paths of lists are stored in active_lists (path to that file can be configured).
Paths to lists can be added to active_lists manually or by file action *Activate list aa* and removed by *Deactivate list dd*.
Max number of tasks from one list can be configured.

### Keyword: *ttt*    

Lists all tasks from list given be query - query is path to file with that list. Constant prefix and sufix of path can be configured.
For example if you allways use one extension for lists you can
set it as constant sufix so you won't need to type it. The same works with prefixes - useful for home directory or when you store all lists in one folder.

## Configuration

All configs (except one) are stored in config.py and are commented there. If you use only one file you probably should remove *tt* and *ttt* tags from workflow to not polute searches.

[Alfred]: http://www.alfredapp.com
[TaskPaper]: http://www.hogbaysoftware.com/products/taskpaper
[basic]: http://bvsc.nazwa.pl/img/TodoFlow/basic.png
[query]: http://bvsc.nazwa.pl/img/TodoFlow/query.png
[regexp]: http://bvsc.nazwa.pl/img/TodoFlow/regexp.png
