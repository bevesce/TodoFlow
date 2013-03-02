tell application "Mail"
	set inbox_path to "/path/to/inbox.todo"  -- set it up!
	set person_tag to " @osoba("
	set mail_tag to " @mail("
	set in_tag to " @in("
	set sel to get selection
	set tasks to {}
	repeat with msg in sel
		set {year:y, month:m, day:d} to msg's date received
		if ((m as integer) < 10) then
			set m to "0" & (m as integer)
		end if
		if ((d as integer) < 10) then
			set d to "0" & (d as integer)
		end if
		set dd to in_tag & y & "-" & m & "-" & d & ")"
		set task to "- " & msg's subject & dd & person_tag & msg's sender & ")" & mail_tag & "message://%3c" & msg's message id & "%3e)"
		if not (task is in tasks) then
			set end of tasks to task
		end if
	end repeat
	set AppleScript's text item delimiters to return
	do shell script "echo " & quoted form of (tasks as string) & " >> " & inbox_path
end tell
