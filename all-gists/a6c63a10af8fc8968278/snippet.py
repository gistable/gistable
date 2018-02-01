# via http://stackoverflow.com/questions/14903664/determine-unique-from-email-addresses-in-maildir-folder

import mailbox
import email

mbox = mailbox.mbox('DADEOL/AOL Mail sorted/Saved.DADEOL Sent.mbox')

uniq_emails = set(email.utils.parseaddr(msg['to'])[1].lower() for msg in mbox)

for a in uniq_emails:
    print a

print len(uniq_emails)
