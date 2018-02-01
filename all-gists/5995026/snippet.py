#!/usr/bin/env python
import plistlib
from shutil import copy
import subprocess
import os
from tempfile import gettempdir
import sys
import atexit

BOOKMARKS_PLIST = '~/Library/Safari/Bookmarks.plist'
bookmarksFile = os.path.expanduser(BOOKMARKS_PLIST)

# Make a copy of the bookmarks and convert it from a binary plist to text
tempDirectory = gettempdir()
copy(bookmarksFile, tempDirectory)
bookmarksFileCopy = os.path.join(tempDirectory, os.path.basename(bookmarksFile))

def removeTempFile():
    os.remove(bookmarksFileCopy)

atexit.register(removeTempFile) # Delete the temp file when the script finishes

converted = subprocess.call(['plutil', '-convert', 'xml1', bookmarksFileCopy])

if converted != 0:
    print "Couldn't convert bookmarks plist from xml format"
    sys.exit(converted)

plist = plistlib.readPlist(bookmarksFileCopy)
 # There should only be one Reading List item, so take the first one
readingList = [item for item in plist['Children'] if 'Title' in item and item['Title'] == 'com.apple.ReadingList'][0]

if 'Children' in readingList:
    for item in readingList['Children']:
        print item['URLString']
