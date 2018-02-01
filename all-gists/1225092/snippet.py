#!/usr/bin/env python

#
# Check if a website is loading and contains a nominated string.
#
# Usage:
#  site-up.py http://example.com/ 'text to search for'
#


import errno
import re
import sys
import time
import urllib

url = sys.argv[1]
search = sys.argv[2]

start = 0
end = 0;

f = urllib.urlopen(url)
start = time.time()
page = f.read()
end = time.time()
f.close()

err = ''
exitCode = 0
matches = re.search(search, page)
if matches is None:
  err = "\nSearch string not found"
  exitCode = errno.ENOENT

print 'Page loaded in {time}s.{error}'.format(time=round(end-start, 2), error=err)

sys.exit(exitCode)
