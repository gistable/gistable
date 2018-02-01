#!/usr/bin/python

"""
Who owns the OUI? IEEE knows.
Run with -u to force update.
"""

from __future__ import print_function
from urllib import urlopen
import sys
import time
import os
import re

class OuiSearch:

    def __init__(self,**kwargs):
        self.query =  "".join(kwargs['q'].split(':')[:3])
        self.cache = os.path.join(os.environ['HOME'], ".oui-cache")
        self.url = "http://standards.ieee.org/develop/regauth/oui/oui.txt"
        self.tempfile = self.cache + '.download'
        self.cache_expire = 86400 * 365
        if time.time() - os.stat(self.cache).st_ctime > self.cache_expire:
            self.refresh()

    def refresh(self):
        """
        Update our local file from the IEEE OUI
        list
        """
        print(">>> Updating Cache", file=sys.stderr)

        if os.path.isfile(self.cache):
            self.run()
            os.remove(self.cache)

        with open(self.tempfile, 'w') as outfile:
            for lne in urlopen(self.url).readlines():
                outfile.write(lne)

        os.rename(self.tempfile, self.cache)

        print(">>> Done", file=sys.stderr)


    def run(self):
        """
        Perform our query.
        """
        with open(self.cache, 'r') as oui_list:
            for line in iter(oui_list):
                if re.search(self.query, line, re.IGNORECASE):
                    print(line)



if sys.argv[1] == '-u':
    user_input = sys.argv[2]
else:
    user_input = sys.argv[1]

search = OuiSearch(q=user_input) 

if sys.argv[1] == '-u':
    search.refresh()

search.run()