# TodoFlow 5

![](icon.png)

TodoFlow is Python module that provides functions to parse, filter, search and modify todo lists stored in plain text files with TaskPaper syntax.

## Changelog

- 2016-10-08 - 5.0.0
    + updates to [TaskPaper 3](https://www.taskpaper.com) queries!
    + drops dependency on [ply](https://github.com/dabeaz/ply)
    + removes separation between `Node`s and `Todos`
    + removes printers and file reading methods
- 2015-10-02 - 4.0.2 
- 2015-04-24 - Removal of workflows
- 2014-10-24 - Release of version 4

## Installation

    pip install TodoFlow

## Overview

TodoFlow is based on two classes: `Todos` and `Todoitem`.

### Todos

`Todos` is a tree-like collection of todo items. `Todos` have list of `subitems` and one `todoitem` (except tree root that doesn't have one).

#### Creating todos

You can create todos from string:

```
from todoflow import Todos
todos = todoflow.Todos("""
project 1:
    - task 1
    - task 2 @today
""")
```

#### Saving todos

You can stringify todos in order to write them to a file:

```
>>> print(todos)
project 1:
    - task 1
    - task 2 @today
project 2:
    - task 3
```

#### Filtering todos

TodoFlow tries to provide the same queries as [TaskPaper 3](https://guide.taskpaper.com/formatting_queries.html). If something doesn't work the same way please create an Issue.

```
>>> today = todos.filter('/*/@today')
>>> print(today)
project 1:
    - task 2 @today
```

- `todos.filter(query)` - Returns new `Todos`, with items, that match given query, or are parent of one. It's analogous to how TaskPaper app works.
- `todos.search(query)` - Returns iterator of `Todos` that match query (and only them).

### Todoitem

`Todoitem`s belong to `Todos` and have methods to modify them and to retrive data from them:

- `tag(tag_to_use, param=None)`
- `remove_tag(tag_to_remove)`
- `has_tag(tag)`
- `get_tag_param(tag)`
- `get_type(tag)`
- `get_text()`
- `get_line_number()`
- `get_line_id()`
- `edit(new_text)`
- `change_to_task()`
- `change_to_project()`
- `change_to_note()`

They can be mutaded, then and those changes are visible in every `Todos` that they belong to.

```
>>> for item in todos.search('@today'):
>>>     item.tag('@done', '2016-10-08')
>>>     item.remove_tag('@today')
>>> print(todos)
project 1:
   - task 1
   - task 2 @done(2014-10-24)
```

## textutils

Module `todoflow.textutils` provides functions
that operate on strings and are used internally in TodoFlow but can be useful outside of it:

- `is_task(text)`
- `is_project(text)`
- `is_note(text)`
- `has_tag(text, tag)`
- `get_tag_param(text, tag)`
- `remove_tag(text, tag)`
- `replace_tag(text, tag, replacement)`
- `add_tag(text, tag, param=None)`
- `enclose_tag(text, tag, prefix, suffix=None)`
- `get_all_tags(text, include_indicator=False)`
- `modify_tag_param(text, tag, modification)`
- `sort_by_tag_param(texts_collection, tag, reverse=False)`
