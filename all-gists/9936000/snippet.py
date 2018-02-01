import notification
from random import randint
import sys
import urllib
import webbrowser

reminders = ["Reminder A", ["Reminder B", "url://"], "Reminder C"]

n = randint(0, len(reminders)-1)
URL = "pythonista://random_reminders.py?action=run"

if type(reminders[n]) == list:
	random_reminder = reminders[n][0]
	URL = URL + "&argv=" + urllib.quote(reminders[n][1], safe = "")
else:
	random_reminder = reminders[n]

d = 60*60*24
random_delay = randint(d, 7*d)

notification.schedule(random_reminder, random_delay, "", URL)

try:
	webbrowser.open(sys.argv[1])
except:
	pass
