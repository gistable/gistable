#!/usr/bin/python2
# Based on: https://bbs.archlinux.org/viewtopic.php?pid=962423#p962423
# This version is modified to handle mailboxes with spaces in the names

import pyinotify
import pynotify
from os.path import expanduser
from mailbox import MaildirMessage
from email.header import decode_header
from gtk.gdk import pixbuf_new_from_file

maildir_folder = expanduser(r"~/Mail/")
notification_timeout = 12000
unread_mail_icon = r"/usr/share/icons/oxygen/32x32/status/mail-unread-new.png"

# Getting the path of all the boxes
fd =  open(expanduser(r"~/.mutt/mailboxes"), 'r')
# [10:-1] to remove the initial '^mailboxes '
boxes = filter(None, (b.rstrip().replace('+','') for b in fd.readline()[10:-1].split('"')))
fd.close()

pynotify.init(r'email_notifier.py')

# Handling a new mail
icon = pixbuf_new_from_file(unread_mail_icon)
dec_header = lambda h : ' '.join(unicode(s, e if bool(e) else 'ascii') for s, e in decode_header(h))

def newfile(event):
    fd = open(event.pathname, 'r')
    mail = MaildirMessage(message=fd)
    From = "From: " + dec_header(mail['From'])
    Subject = "Subject: " + dec_header(mail['Subject'])
    n = pynotify.Notification("New mail in "+'/'.join(event.path.split('/')[-3:-1]), From+ "\n"+ Subject)
    fd.close()
    n.set_icon_from_pixbuf(icon)
    n.set_timeout(notification_timeout)
    n.show()

wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, newfile)

for box in boxes:
    wm.add_watch(maildir_folder+box+"/new", pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO)

notifier.loop()