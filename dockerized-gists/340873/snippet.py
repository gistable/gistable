#! /usr/bin/python -tt
"""Generate a sup contacts list from abook"""

import configobj
import os
import sys

def parse(file=None):
    if not file:
        file = os.path.expanduser("~/.abook/addressbook")
    conf = configobj.ConfigObj(file, list_values=False)
    for chunk in filter(lambda d: "nick" in d and "email" in d, conf.values()):
        print "%(nick)s: %(name)s" % chunk, \
            "<%s>" % chunk["email"].split(",")[0]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print "%s [addressbook]" % sys.argv[0]
            sys.exit(255)
        addressbook = sys.argv[1]
    else:
        addressbook = None
    parse(addressbook)