#!/usr/local/bin/python2.6

"""
mailbox2script.py

This is a replacement for WebFaction's built-in mail2script (which cannot
parse large messages > 5MB).

To use it:

    1. Create an email address that sends messages to a mailbox.

    2. Save this script to your WebFaction server and set the mailbox name,
       mailbox password, and path to your script.

    3. Create a cron job to run this script at a suitable interval, eg:

       */5 * * * * /usr/local/bin/python2.6 /home/username/bin/mailbox2script.py > /dev/null 2>&1

Whenever it runs, it will fetch messages that it has not already processed and
pass them to stdin of the script identified by script_path.
"""

import imaplib
import subprocess

mailbox = 'your_mailbox_name'
passwd = 'your_mailbox_password'
imaphost = 'mail.webfaction.com'
script_path = '/home/username/path/to/your/script'

# log into the mailbox
server = imaplib.IMAP4_SSL(imaphost)
server.login(mailbox,passwd)

# get all unprocessed messages
server.select()
resp, items = server.search(None, "UNSEEN")
items = items[0].split()

# fetch messages and send them to the script
for i in items:
    resp, data = server.fetch(i, "(RFC822)")
    text = data[0][1].replace('\r','')
    p = subprocess.Popen([script_path],stdin=subprocess.PIPE)
    p.stdin.write(text)
    p.stdin.close()
