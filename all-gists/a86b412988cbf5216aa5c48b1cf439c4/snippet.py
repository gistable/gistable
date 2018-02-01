import re
import clipboard
import console
import webbrowser
import urllib
import contacts
import datetime
import dialogs

def extract_num(input):
		match = re.findall("[0-9*]",input)
		return ''.join(match)

# Fetch text from clipboard and extract what looks like a phone number
input = clipboard.get()
match = re.search("[0-9\+\-\ ]{7,}",input)
output = match.group(0)
clipboard.set(output)
console.hud_alert(output,icon='success',duration=1)
		
# Check if the number exists in the phonebook
people = contacts.get_all_people()
found = False
for p in people:
	for n in p.phone:
		# Numbers can be stored strangely in contacts so just check the last 9 digits
		num = extract_num(output)
		cleannum = extract_num(n[1])
		if (num[-9:] == cleannum[-9:]):
			found = True

# Pop a form to add the contact if not found
if not found:
	fields = [ {'type':'text','key':'first','value':'','title':'First Name'},{'type':'text','key':'last','value':'','title':'Last Name'},{'type':'text','key':'org','value':'','title':'Organisation'},{'type':'text','key':'num','value':output,'title':'Number'},	{'type':'text','key':'note','value':'Added by Make Call script on '+datetime.datetime.now().ctime(),'title':'Notes'} ]
	fields = dialogs.form_dialog('Add a Contact', fields)
			
	newContact = contacts.Person()
	newContact.note = fields['note']
	newContact.first_name = fields['first']
	newContact.last_name = fields['last']
	newContact.organization = fields['org']
	newContact.phone = [(contacts.WORK,fields['num'])]
	contacts.add_person(newContact)
	contacts.save()

# Call the number
webbrowser.open('tel:'+urllib.quote(output))