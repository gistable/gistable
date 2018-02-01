#!/usr/bin/env python


import time
import urllib
import urllib2
import cookielib

start_time = time.time()
COOKIEFILE = 'cookiejar.txt'
NOCOOKIES = False

# setup cookies
cj = cookielib.LWPCookieJar()

try:
    cj.load(COOKIEFILE)
except cookielib.LoadError:
    NOCOOKIES = True

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

if NOCOOKIES:
    d = urllib.urlencode({'username': 'my_username', 'password': '1234myPassword'})
    opener.open("http://www.example.com/login/")
    opener.open("http://www.example.com/login/", d)
    cj.save(filename=COOKIEFILE, ignore_discard=True, ignore_expires=True)

end_time = time.time()
elapsed = end_time - start_time
print "Loging in took %s seconds" % round(elapsed / 60, 4)