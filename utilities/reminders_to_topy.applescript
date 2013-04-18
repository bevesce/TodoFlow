on dateToISO(d)
	if d is missing value then
		return "missing value"
	end if
	set {year:y, month:m, day:d} to d
	set m to m as integer
	if (m < 10) then
		set m to "0" & (m as string)
	end if
	if ((d as integer) < 10) then
		set d to "0" & (d as integer)
	end if
	return y & "-" & m & "-" & d
end dateToISO

tell application "Reminders"
	set res to "["
	tell list "Inbox"
		set todos to (get reminders)
		repeat with todoItem in todos
			set todoStr to "{"
			set todoStr to todoStr & "\"name\": \"" & name of todoItem & "\","
			set todoStr to todoStr & "\"completed\": " & completed of todoItem & ","
			set todoStr to todoStr & "\"body\": \"" & body of todoItem & "\","
			set todoStr to todoStr & "\"priority\": \"" & priority of todoItem & "\","
			set todoStr to todoStr & "\"creation_date\": \"" & my dateToISO(creation date of todoItem) & "\","
			set todoStr to todoStr & "\"due_date\": \"" & my dateToISO(due date of todoItem) & "\","
			set todoStr to todoStr & "\"remind_me_date\": \"" & my dateToISO(remind me date of todoItem) & "\","
			set todoStr to todoStr & "\"completion_date\": \"" & my dateToISO(completion date of todoItem) & "\""
			set todoStr to todoStr & "}"
			set res to res & todoStr & ","
			delete todoItem
		end repeat
	end tell
	set num to (count of characters of res)
	set res to (characters 1 thru (num - 1) of text of res) as text
	set res to res & "]"
	do shell script "python /Users/bvsc/Dropbox/TODO/scripts/topy/utilities/reminder_in.py " & (quoted form of res)
end tell