MAIL_SERVER = ''
USERNAME = ''
PASSWORD = ''
MAILBOX = 'Spam'
MAX_DAYS = 7 # Deletes messages older than a week

import imaplib
import datetime

today = datetime.date.today()
cutoff_date = today - datetime.timedelta(days=MAX_DAYS)
before_date = cutoff_date.strftime('%d-%b-%Y')

search_args = '(BEFORE "%s")' % before_date

imap = imaplib.IMAP4(MAIL_SERVER)
imap.login(USERNAME, PASSWORD)
imap.select(MAILBOX)

typ, data = imap.search(None, 'ALL', search_args)

for num in data[0].split():
    imap.store(num, '+FLAGS', '\\Deleted')

imap.expunge()

imap.close()
imap.logout()