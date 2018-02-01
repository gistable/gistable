# QuickReminder 3.0.2 - see: http://jarrodwhaley.com/other-projects/geekery/


import sys
import urllib.request, urllib.parse, urllib.error
import notification
import console
import webbrowser

# Get arguments, if any
numArgs = len(sys.argv)

# Set Drafts URL
url = 'drafts4://x-callback-url/create?text=' + ''

# Convert minutes to integer, strip commas if present
def intconv(arg):
	arg = arg.replace(",", "")
	return int(arg) * 60

# Routes and processes input, either directly from prompts
# or from Drafts.

if numArgs == 1:
	text = console.input_alert('Remind you to...')
	digit = console.input_alert('In how many minutes?')
	interval = intconv(digit)
	url = ''
elif numArgs > 1 and (sys.argv[2]) == '':
	digit = console.input_alert('In how many minutes?')
elif numArgs == 3:
	text = sys.argv[1]
	digit = sys.argv[2]
	interval = intconv(digit)
else:
	console.alert('Failed.')
	
# Confirm before scheduling
console.alert('Schedule?', 'Alert in' + ' ' + digit + ' ' + 
'minutes?', 'Schedule')

# Schedule
notification.schedule(text, interval, 'default')

# Send back to Drafts if input sent from there.
# Show confirmation HUD if not.

if len(url) > 1:
	webbrowser.open(url)
	notification.schedule('Scheduled.', 0.5, 'default')
else:
	console.hud_alert('Scheduled.')