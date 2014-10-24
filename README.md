# Todoflow 4.0

![](workflows/img/task_icon.png)

Todoflow is Python module that provides functions to parse, filter, search, modify and save todo lists stored in plain text files with TaskPaper syntax.

## Changelog

- 2014-10-24 - Release of version 4
    - new code base
    - queries are now parsed with [ply](https://github.com/dabeaz/ply)
    - for now removes support for [Editorial.app](http://omz-software.com/editorial/)
    - workflows start from zero
    - new icons
    - setup.py

## Installation

    pip install git+https://github.com/bevesce/TodoFlow.git

## Overview

### Loading todos

Load and parse todos using one of this functions:

- `todos = todoflow.from_text(text)`
- `todos = todoflow.from_path(path)`
- `todos = todoflow.from_paths(paths)` - todos from several files are joined into one
- `todos = todoflow.from_dir(path, extension='.taskpaper')` - every todo file in given direcotry is joined into one todos

### Saving todos

- `todoflow.to_path(todos, path)` - save todos to file
- `todoflow.to_sources(todos)` - when todos are loaded from file (using `from_path`, `from_paths` or `from_dir`) they store path to source file so they can be saved to it later

### Todos

- `todos.filter`
- `todos.search`

#### Queries

- text
- @tag
- @tag *op arg*
- project, type, uniqueid *op arg*
- +d, +f
- =, <=, <, >, >=, !=, ->, <-
- and, or, not

### Todo item

- `tag(tag_to_use, param=None)`
- `remove_tag(tag_to_remove)`
- `has_tag(tag)`
- `get_tag_param(tag)`
- `edit(new_text)`
- `change_to_task()`
- `change_to_project()`
- `change_to_note()`
- `change_to_empty_line()`

## textutils

Module `todoflow.textutils` provides functions
that operate on text and are used internally in todoflow but can be
useful outside of it:

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