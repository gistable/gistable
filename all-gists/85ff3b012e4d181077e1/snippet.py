#!/usr/bin/env python
import imaplib
import email
import json
import re
from getpass import getpass

label = "undelivered-mails"
username = "user@gmail.com"
addrfilename = 'failed-addresses.txt'
diagnosticsfilename = 'failed-addresses-diagnostics.txt'

qmail_send_pattern = re.compile('^.*qmail-send.*$', re.MULTILINE)
qmail_err_pattern = re.compile('^<([a-zA-Z0-9_+.-]+@[a-zA-Z0-9_+.-]+)>:\s*$(.*?)^--- ', re.MULTILINE | re.DOTALL)

#testinput = """Hi. This is the qmail-send program at pop3.aspecthosting.net.
#I'm afraid I wasn't able to deliver your message to the following addresses.
#This is a permanent error; I've given up. Sorry it didn't work out.
#
#<blah@example.com>:
#Sorry, no mailbox here by that name. (#5.1.1)
#
#--- Below this line is a copy of the message."""

def parse_qmail_bounce(txt):
	if qmail_send_pattern.match(txt) == None:
		return None
	match = qmail_err_pattern.search(txt)
	if match == None:
		return None
	
	final_recipient = match.group(1)
	diagnostic_code = match.group(2)
	return (final_recipient, diagnostic_code.strip())

err_code_pattern = re.compile('(\d\d\d[ -].*)')

def find_diag_in_text(part):
	text = part.get_payload()
	match = err_code_pattern.search(text)
	if match == None:
		return None
	return match.group(1)

def get_error_info(mail, uid):
	result, data = mail.uid('fetch', uid, '(RFC822)')
	if result != 'OK':
		print "Fetch of " + uid + " failed"
		exit()
	eml = data[0][1]
	message = email.message_from_string(eml)
	payload = message.get_payload()
	original_recipient = None
	final_recipient = None
	diagnostic_code = None

	if not message.is_multipart():
		res = parse_qmail_bounce(payload)
		if res != None:
			return res
		print "non-multipart message with uid " + uid + ":\n" + payload
		return (None, payload)
	for part in payload:
		if part.get_content_type() != 'message/delivery-status':
			continue
		delivery_status_body = part.get_payload()
		for subpart in delivery_status_body:
			if original_recipient == None:
				final_recipient = subpart.get('Original-Recipient')
			if final_recipient == None:
				final_recipient = subpart.get('Final-Recipient')
			if diagnostic_code == None:
				diagnostic_code = subpart.get('Diagnostic-Code')
	# final_recipient looks like: 'rfc822; 22se.preben@gmail.com' 
	if diagnostic_code == None:
		plaintextparts = [part for part in payload if part.get_content_type() == 'text/plain']
		for part in plaintextparts:
			diagnostic_code = find_diag_in_text(part)
			if diagnostic_code != None:
				break
		if diagnostic_code == None and len(plaintextparts) > 0:
			diagnostic_code = plaintextparts[0].get_payload()
	if original_recipient != None:
		recipient = original_recipient
	else:
		recipient = final_recipient
	if recipient != None:
		rparts = [s.strip() for s in recipient.split(';')]
		recipient = rparts[-1]
	if recipient[0] == '<' and recipient[-1] == '>':
		recipient = recipient[1:-1]
	return (recipient, diagnostic_code)

def login():
	password = getpass(prompt="Password: ")
	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(username, password)
	return mail

mail = login()
mail.select(label)
result, data = mail.uid("search", None, "ALL")
if result != 'OK':
	print "Search failed: " + result
	exit()

uids = data[0].split()
#print(len(uids))
#exit()

addrfile = open(addrfilename, 'w')
diagnosticsfile = open(diagnosticsfilename, 'w')
diagnosticsfile.write('[\n')

for uid in uids:
	recipient, diagnostic_code = get_error_info(mail, uid)
	if recipient != None:
		addrfile.write(recipient + '\n')
	diagnosticsfile.write(json.dumps([recipient, diagnostic_code]))
	diagnosticsfile.write(',\n')

diagnosticsfile.write(']')
