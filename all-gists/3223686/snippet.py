#!/usr/bin/python

import sys
import os
from urllib import urlencode
import subprocess

# setClipboardData is from <http://www.macdrifter.com/2011/12/python-and-the-mac-clipboard/>*/

def setClipboardData(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()

searchString = " ".join(sys.argv[1:])
searchString = "http://www.google.com/search?" + urlencode({'q':searchString})

setClipboardData(searchString)
