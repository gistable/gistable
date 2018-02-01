#!/usr/bin/python

"""Module for pulling contacts out of Google and storing them to disk
(or something).

See the official guide for a more in-depth look at GData Python
   http://code.google.com/apis/contacts/docs/1.0/developers_guide_python.html
"""

import atom
import gdata.contacts
import gdata.contacts.service
import getpass
import sys

def printFeed(feed):
    for entry in feed.entry:
        nick = ""
        name = entry.title.text
        for email in entry.email:
            print('%s\t%s\t"%s" <%s>' % (nick, name, name, email.address))

def main(args):
    def usage():
        print("""usage: pull_contacts.py <email>
""")

    if len(args) < 1:
        usage()
        exit(1)

    gd_client = gdata.contacts.service.ContactsService()
    gd_client.email = args[0]
    gd_client.password = getpass.getpass()
    gd_client.source = "abstractbinary.org-pull_contacts-1"
    gd_client.ProgrammaticLogin()

    query = gdata.contacts.service.ContactsQuery()
    query.max_results = 1000
    contacts = gd_client.GetContactsFeed(query.ToUri())
    printFeed(contacts)

if __name__ == "__main__":
    main(sys.argv[1:])
