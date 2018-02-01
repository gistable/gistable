#!/usr/bin/env python

import imaplib
import getpass
import os
import argparse
import sys

__productname__ = 'grabmsg'
__version__     = "0.1"
__copyright__   = "Copyright 2012 Stuart Carnie"
__author__      = "Stuart Carnie"
__author_email__= "stuart.carnie@gmail.com"
__description__ = "Utility to grab email messages by UID"
__license__  = "Licensed under the MIT license"


def grabmsg():
    parser = argparse.ArgumentParser(description="%s.\n\n%s" %
                                                  (__copyright__,
                                                   __license__))
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--user', '-u', help='user id for IMAP server')
    parser.add_argument('--pass', '-p', help='password for IMAP server; omit for prompt', dest='password')
    parser.add_argument('--folder', '-f', help='folder; default=inbox', dest='folder', default='inbox')
    parser.add_argument('uids', help='list of uids to grab', nargs='+', metavar='uid')

    options = parser.parse_args()

    if options.password is None:
        options.password = getpass.getpass('Enter password:')

    if options.uids is None:
        sys.exit(1)

    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(options.user, options.password)
        result, data = imap.select(options.folder)
        if result != 'OK':
            print("Invalid folder, %s" % options.folder)
            exit(1)

        for uid in options.uids:
            try:
                result, msg = imap.fetch(uid, '(RFC822)')
                msg = msg[0][1] # msg content
                filename = '%s.%s.txt' % (options.folder, uid)
                print('writing %s' % filename)
                with open(filename, 'wt') as f:
                    f.write(msg)
            except Exception as e:
                print("failed: %s" % e)
        imap.logout()
    except Exception as e:
        print("failed: %s" % e)
        pass


if __name__ == '__main__':
    grabmsg()