#!/usr/bin/env python

# Don't forget to enable the Chat label in the source account as visible to IMAP.

import getpass 
from imapclient import IMAPClient

def main():
    s_username = raw_input("Source Email: ")
    s_password = getpass.getpass(prompt="Source Password: ")
    d_username = raw_input("Destination Email: ")
    d_password = getpass.getpass(prompt="Source Password: ")
    certain = raw_input("Run it for real? (yes/*)")
    destination_folder = 'Migrated Chatlogs' 

    # source server
    source = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
    source.login(s_username, s_password)

    # destination server
    destination = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
    destination.login(d_username, d_password)

    select_info = source.select_folder("[Gmail]/Chats", readonly=True)
    print 'Migrating %s chat messages' % select_info['EXISTS']
    print 'Why don\'t you go grab a cup of coffee.. this is going to take a while'

    chats = source.search(['NOT DELETED'])

    if not destination.folder_exists(destination_folder):
        print "creating %s " % destination_folder
        destination.create_folder(destination_folder)

    for message in chats:
        print message
        fetchData = source.fetch(int(message),['INTERNALDATE','FLAGS', 'RFC822'])[message]
        if certain == "yes":
            destination.append(destination_folder,
                msg=fetchData['RFC822'],
                flags=fetchData['FLAGS'],
                msg_time=fetchData['INTERNALDATE'])

    destination.logout()
    source.logout() 

if __name__ == '__main__':
    main()
