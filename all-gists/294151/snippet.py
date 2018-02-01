#!/usr/bin/env python
"""Outputs the WebKit cookies for a specified URL.
Useful for wget'ing URLs which require authentication.

$ python thisfile.py http://example.com > wgetcookies.txt
$ wget --load-cookies wgetcookies.txt http://example.com/example.zip
"""

import objc
from Foundation import NSHTTPCookieStorage, NSURL
import sys
import os
from StringIO import StringIO
 
FILE_HEADER = """# HTTP Cookie File 
"""
 
def get_cookiefile_for_url(url):
    """
    Returns WebKit cookies for the specified URL as a string.
    Modified from http://zerokspot.com/weblog/2007/04/12/safari-cookies-to-netscape-cookie-format/
    """
    storage = NSHTTPCookieStorage.sharedHTTPCookieStorage()
    u = NSURL.URLWithString_(url)
    fd = StringIO()
    try:
        fd.write(FILE_HEADER)
        for c in storage.cookiesForURL_(u):
            line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                c.domain(),
                'TRUE',
                c.path(),
                str(bool(c.isSecure())).upper(),
                int(c.expiresDate().timeIntervalSince1970()),
                c.name(),
                c.value(),
            )
            fd.write(line)
    finally:
        fd.seek(0)
        return fd.read()

if len(sys.argv) != 2:
    print "Usage: %s <url>" % sys.argv[0]
    sys.exit(1)

print get_cookiefile_for_url(sys.argv[1])
