# To Calendar

For every task tagged with *@due* or *@date* creates coresponding event in Calendar.app in proper calendar. After running this *@calendar* tag is added to item so it won't create duplicates. More event details can be specified using other tags:

- *@due(YYYY-MM-DD)* or *@remind(YYYY-MM-DD)*
- *at(hh:mm)* or *at(hh:mm-hh:mm)* - start time and optional end time, default duration is one hour, if no start time is provided it's assumed that it is all day event
- @place(location)
