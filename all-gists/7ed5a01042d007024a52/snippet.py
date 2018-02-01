import imaplib

EMAIL_ADDRESS = 'dummy@nowhere.net'
PASSWORD = 'nope nope nope'
FOLDER = 'This_is_a_parent_label/this_is_a_sublabel'

while True:
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select(FOLDER)
        mail.store("1:*", '+X-GM-LABELS', '\\Trash')
        mail.expunge()
    except imaplib.IMAP4.abort as e:
        print "Imap abort, restarting for the rest of the mails: {msg}".format(msg=str(e))
        continue
    break
