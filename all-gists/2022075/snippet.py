#!/usr/bin/env python
#-*- coding:utf-8 -*-

import imaplib
import getpass
import argparse

argparser = argparse.ArgumentParser(description="Dump a IMAP folder into .eml files")
argparser.add_argument('-s', dest='host', help="IMAP host, like imap.gmail.com", required=True)
argparser.add_argument('-u', dest='username', help="IMAP username", required=True)
argparser.add_argument('-r', dest='remote_folder', help="Remote folder to download", default='INBOX')
argparser.add_argument('-l', dest='local_folder', help="Local folder where to save .eml files", default='.')
args = argparser.parse_args()

gmail = imaplib.IMAP4_SSL(args.host)
gmail.login(args.username, getpass.getpass())
gmail.select(args.remote_folder)
typ, data = gmail.search(None, 'ALL')
for num in data[0].split():
    typ, data = gmail.fetch(num, '(RFC822)')
    f = open('%s/%s.eml' %(args.local_folder, num), 'w')
    print >> f, data[0][1]
gmail.close()
gmail.logout()