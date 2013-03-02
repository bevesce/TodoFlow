# SublimeTodoFlow #

# Overview #

SublimeText2 package for working with todo lists in plain text files with [taskpaperlike][] [format][]. It's designed to work with every color scheme. I don't like when packages overwrite my theme.

![sublime1][]![sublime2][]![sublime3][]![sublime4][]

# Key Binding & Commands #

- ⌘+⌃+↩ / *ctrl+alt+enter* - toggle between **@next** / **@today** / **@done(YYYY-MM-DD)** / … tags. ⌘+D is for selecting words, how could anyone overwrite that?
- ⌘+↩ / *ctrl+enter* - insert new task
- ⌘+⌃+, / *ctrl+alr+,* - change type of current line (toggle between task / project / note)
- ⌘+⌃+. / *ctrl+alr+.* - add tag from quick panel, list of tags is created from tags in current file, tags **@in**, **@due**, **@done** are not included.

![sublime5][]

# File format [format]#

Package automatically works with files with .todo and .taskpaper extension.

- Task is line that begins with '- ', can be indented with tabs.
- Project is every line that is not task and ends with ':' with eventual trailings tags after that colon.
- Every other line is a note.
- Tag is word preceded by '@' with eventual parameter in parenthesis (e.g. **@today**, **@done(2013-03-01)**).
- Structure of list is defined by indentation levels of items.

© 2013 Piotr Wilczyński
[@bevesce][]

[@bevesce]: https://twitter.com/@bevesce
[taskpaperlike]: http://www.hogbaysoftware.com/products/taskpaper
[sublime1]: http://bvsc.nazwa.pl/img/TodoFlow/sublime3.png
[sublime2]: http://bvsc.nazwa.pl/img/TodoFlow/sublime2.png
[sublime3]: http://bvsc.nazwa.pl/img/TodoFlow/sublime1.png
[sublime4]: http://bvsc.nazwa.pl/img/TodoFlow/sublime4.png
[sublime5]: http://bvsc.nazwa.pl/img/TodoFlow/sublime5.png
