#!/usr/bin/env python
# -*- coding: utf-8 -*-
# addnote.py by JP Mens (September 2015), inspired by Martin Schmitt
# Usage: addnote subject "body (may be empty") [image ...]
# Adds a Notes.app (OSX and iOS) compatible message to the "Notes"
# IMAP folder. The IMAP store is configured from a file called
# `creds':
#
#   [imap]
#   hostname = 
#   username = 
#   password = 
# 

import imaplib
import ConfigParser
import os
import sys
import time
import mimetypes
import email.message
import email.utils
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import uuid

def imap_open(verbose=False):
    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser('creds')])

    # Connect to the server
    hostname = config.get('imap', 'hostname')
    if verbose: print 'Connecting to', hostname
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config.get('imap', 'username')
    password = config.get('imap', 'password')
    if verbose: print 'Logging in as', username
    connection.login(username, password)
    return connection

def new_message(subj, body, filenames=None):

    guid = str(uuid.uuid4()).upper()
    date_string = email.utils.formatdate(time.time(), localtime=True)

    msg = MIMEMultipart('related', 'Apple-Mail-%s' % uuid.uuid4(), content_type='text/html')
    msg['Subject']                      = subj
    msg['From']                         = 'jp@example.com'
    msg['To']                           = 'jp@example.com'
    msg['X-Uniform-Type-Identifier']    = 'com.apple.mail-note'
    msg['Content-Transfer-Encoding']    = '7bit'
    msg['Mime-Version']                 = '1.0'
    msg['Date']                         = date_string  # Last modif time
    msg['X-Mail-Created-Date']          = date_string   # Creation time
    msg['X-Universally-Unique-Identifier']  = guid
    msg['Message-Id']                    = "<%s@bot.ww.mens.de>" % guid

    # We have to know the CID of all attachments for the first MIME part
    objects = {}
    if filenames:
        for filename in filenames:
            objects[filename] = "%s@example.org" % str(uuid.uuid4())

    # Notes have the subject in the first line of the body.
    html_body = "%s\n<div>%s\n" % (subj, body)
    if len(objects):
        html_body = html_body

        # OSX will show the attachment without the <object>
        # but iOS won't. Of course.
        for k in objects:
            id = objects[k]
            o = '<object type="application/x-apple-msg-attachment" data="cid:%s"></object>' % id
            html_body = html_body + o

    html_body = html_body + "</div>"

    body_part = MIMEText(html_body, 'html') # , 'utf-8')
    msg.attach(body_part)

    # Now for the attachments, if we have any.

    if filenames:
        for filename in filenames:
            cid = objects[filename]
            ctype, encoding = mimetypes.guess_type(filename)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            data = open(filename, 'rb').read()
            img_t = {
                '_subtype'          : subtype,
                'name'              : os.path.basename(filename),
                'x-apple-part-url'  : cid,
            }
            attachment = MIMEImage(data, **img_t)
            attachment.add_header('Content-ID', "<%s>" % cid)
            attachment.add_header('Content-Disposition', 'inline', filename=os.path.basename(filename))
            msg.attach(attachment)


    return msg

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s subject bodytext [imagefile ...]" % sys.argv[0]
        sys.exit(1)

    subject = sys.argv[1]
    body = sys.argv[2]
    files = sys.argv[3:]

    msg = new_message(subject, body, files)

    c = imap_open(verbose=True)

    try:
        c.select('Notes')
        c.append('Notes', '', imaplib.Time2Internaldate(time.time()), str(msg))
    finally:
        c.close()
        c.logout()
