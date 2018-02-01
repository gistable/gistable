#!/usr/bin/env python

# 1. In Google Voice settings, set it to forward SMS messages to your Gmail.
# 2. Set up a Gmail filter to add a label to SMS messages that you want to
#    auto-reply to (e.g. if they are from a specific sender, if they contain 
#    certain text, etc).
# 3. Fill in gmail address, password, and your target gmail label below.
# 4. Run this from cron to have it periodically check for messages.

from smtplib import SMTP
from imapclient import IMAPClient
import email
from email.mime.text import MIMEText

REPLY_BODY = 'Your autoreply message'

GMAIL_ADDR = 'your.address@gmail.com'
PASSWORD = 'your-gmail-password'

# set up a gmail filter to add the target label to the SMS messages you want to
# send an autoreply
LABEL_TARGET = 'sms_auto'
LABEL_PROCESSED = 'sms_auto/processed'
LABEL_IN_PROCESS = 'sms_auto/processing'

GMAIL_IMAP_SERVER = 'imap.gmail.com'
GMAIL_SMTP_SERVER = 'smtp.gmail.com'
GMAIL_SMTP_PORT   = 587

imap_server = None

def main():
	global imap_server
	imap_server = IMAPClient(GMAIL_IMAP_SERVER, use_uid=True, ssl=True)
	imap_server.login(GMAIL_ADDR, PASSWORD)
	
	messages = get_matching_messages()
	label_as_in_process(messages)
	process_messages(messages)

def get_matching_messages():
	select_info = imap_server.select_folder('[Gmail]/All Mail')
	
	return imap_server.search(['X-GM-LABELS %s' % LABEL_TARGET,
				'NOT X-GM-LABELS %s' % LABEL_PROCESSED,
				'NOT X-GM-LABELS %s' % LABEL_IN_PROCESS])

def label_as_in_process(messages):
	labels_added = imap_server.add_gmail_labels(messages, [LABEL_IN_PROCESS])

def label_as_processed(messages):
	labels_added = imap_server.add_gmail_labels(messages, [LABEL_PROCESSED])
	labels_removed = imap_server.remove_gmail_labels(messages, [LABEL_IN_PROCESS])

def process_messages(messages):
	for message_uid in messages:
		process_message(message_uid)
		label_as_processed([message_uid])

def process_message(message_uid):
	message_str = imap_server.fetch([message_uid], ['RFC822'])[message_uid]['RFC822']
	message = email.message_from_string(message_str)
	from_addr = message['from']
	msg_id = message['message-id']
	subj = message['subject']
	print('Message %s from %s about %s' % (msg_id, from_addr, subj))
	reply_msg = prepare_reply_message(msg_id, from_addr, subj)
	send_email(reply_msg, GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT)
	
def prepare_reply_message(in_reply_to, to_addr, subject):
	reply_msg = MIMEText(REPLY_BODY)
	reply_msg['From'] = GMAIL_ADDR
	reply_msg['To'] = to_addr
	reply_msg['In-Reply-To'] = in_reply_to
	reply_msg['Subject'] = 'Re: %s' % subject
	return reply_msg

def send_email(message,
              smtp_server='smtp.gmail.com', smtp_port=587):
    from_addr = message['from']
    to_addr = message['to']
    server = SMTP('%s:%d' % (smtp_server, smtp_port))
    server.starttls()
    server.ehlo()
    server.login(GMAIL_ADDR, PASSWORD)
    server.sendmail(from_addr, to_addr, message.as_string())
    server.quit()

if __name__ == "__main__":
	main()
