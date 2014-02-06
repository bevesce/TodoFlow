# Alfred todoflow

Workflow for searching TaskPaper list in Alfred. 

![q keyword](http://procrastinationlog.net/img/alfredq.png)

## Installation

1. Install todoflow
2. Change path to alfredq.py in *Script Filter* in Alfred inside Alfred
3. Probably you'll need to do something to make todoflow module visible from Alfred in *Add list* file action, you can set path in config.py in workflow folder

# Alfred todoflow inbox

Workflow to insert new tasks to Inbox file. Uses *Keyword*, *Fallback Search* and *Hotkey* to insert selected text.

Action:

![in keyword](http://procrastinationlog.net/img/inbox.png)

will insert:

    - write readme for todoflow @in(2014-02-06)

If you using *Mail.app* you can also use *Hotkey* to insert selected mail and it will insert something like this:

    - mail subject @from(name <address>) @mail(message://link_to_mail) @in(2014-02-06)

## Installation

1. Install todoflow
2. Set path to inbox.py in first *Run Script*
3. Set path to Inbox TaskPaper list in AppleScript in second *Run Script*