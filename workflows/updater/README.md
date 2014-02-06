# Updater

Collections of script that I run at the end of the day to update lists.

- log_to_day_one - logs tasks done in that day to Day One
- update_lists
    - update_daily - adds tag *@workingg* to every task in *Daily* project
    - update_waiting - copies tasks tagged with *@waiting(today_date)* to Inbox from Onhold project
    - update_weekly - copies tasks tagged with *@weekly(today_weekday)* to Inbox from Onhold project
    - update_blocked - there are two tags *@blocker(id)* and *@blocked(id)*, when *@blocker(id)* task is *@done* tag *@blocked(id)* is removed from tasks, *id* can be any text
    - update_incremental - if task is tagged with *@v(i)* and *@inc(j)* parameter of *@v* is changed to *i + j*.
    - update_followups - when task with tag *@followup(i task_text)* is *@done* then adds task *- task_text @waiting(today + i days) @following(original_task_text_without_tags)* to Onhold project
- tvcal - adds shows that I watch to Inbox on day when they air, uses [TV Calendar](http://www.pogdesign.co.uk/cat/)
- end_the_day - One to rule them all