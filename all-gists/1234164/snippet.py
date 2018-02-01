#!/usr/bin/env python

import getpass, imaplib, sys
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option('-s', '--save', help='file to save contents to')
    parser.add_option('-d', '--delete', action='store_true',
                      help='delete contents')
    parser.add_option('-u', '--user', help='your umail username')
    (options, args) = parser.parse_args()

    if not options.save and not options.delete:
        parser.error('Either --save or --delete must be provided')

    if options.user:
        user = options.user
    else:
        sys.stdout.write('Username: ')
        user = sys.stdin.readline().strip()

    tries = 0
    while tries < 3:
        tries += 1
        pswd = getpass.getpass()
        try:
            imap = imaplib.IMAP4_SSL('incoming.umail.ucsb.edu', 993)
        except:
            raise

        try:
            imap.login(user, pswd)
            break
        except imap.error, e:
            print e
    else:
        print 'Too many failed attempts, please try again.'
        return 1

    imap.select()
    _, data = imap.search(None, 'ALL')
    msgs = data[0].split()

    if len(msgs) == 0:
        print 'Your UMAIL is empty!'
        return 0
    else:
        print 'Found %d messages' % (len(msgs))

    if options.save:
        save_file = open(options.save, 'w')

    for i in msgs:
        sys.stdout.write('.')
        sys.stdout.flush()
        if options.save:
            _, data = imap.fetch(i, '(RFC822)')
            save_file.write('---MSG #%s---\n%s\n' % (i, data[0][1]))
        if options.delete:
            imap.store(i, '+FLAGS', '\\Deleted')
    print

    if options.save:
        print 'Saved %d messages to %s' % (len(msgs), options.save)
        save_file.close()
    if options.delete:
        _, data = imap.expunge()
        print 'Deleted %d messages' % (len(data))

    imap.close()
    imap.logout()
    return 0

if __name__ == '__main__':
    sys.exit(main())