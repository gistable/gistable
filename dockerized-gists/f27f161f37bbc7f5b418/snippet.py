#!/usr/bin/python
# ReadingListCatcher
# - A script for exporting Safari Reading List items to Markdown and Pinboard
#   Brett Terpstra 2015
# Uses code from <https://gist.github.com/robmathers/5995026>
# Requires Python pinboard lib for Pinboard.in import:
#     `easy_install pinboard` or `pip install pinboard`
import plistlib
from shutil import copy
import subprocess
import os
from tempfile import gettempdir
import sys
import atexit
import re
import time
from datetime import date, datetime, timedelta
from os import path
import pytz

DEFAULT_EXPORT_TYPE = 'pb' # pb, md or all
PINBOARD_API_KEY = 'XXXXXXX:XXXXXXXXXXXXXXXXXXXX' # https://pinboard.in/settings/password
BOOKMARKS_MARKDOWN_FILE = '~/Dropbox/Reading List Bookmarks.markdown' # Markdown file if using md export
BOOKMARKS_PLIST = '~/Library/Safari/Bookmarks.plist' # Shouldn't need to modify

bookmarksFile = os.path.expanduser(BOOKMARKS_PLIST)
markdownFile = os.path.expanduser(BOOKMARKS_MARKDOWN_FILE)

# Make a copy of the bookmarks and convert it from a binary plist to text
tempDirectory = gettempdir()
copy(bookmarksFile, tempDirectory)
bookmarksFileCopy = os.path.join(tempDirectory, os.path.basename(bookmarksFile))

def removeTempFile():
    os.remove(bookmarksFileCopy)

atexit.register(removeTempFile) # Delete the temp file when the script finishes

class _readingList():
    def __init__(self, exportType):

        self.postedCount = 0
        self.exportType = exportType

        if self.exportType == 'pb':
            import pinboard
            self.pb = pinboard.Pinboard(PINBOARD_API_KEY)

        converted = subprocess.call(['plutil', '-convert', 'xml1', bookmarksFileCopy])

        if converted != 0:
            print 'Couldn\'t convert bookmarks plist from xml format'
            sys.exit(converted)

        plist = plistlib.readPlist(bookmarksFileCopy)
         # There should only be one Reading List item, so take the first one
        readingList = [item for item in plist['Children'] if 'Title' in item and item['Title'] == 'com.apple.ReadingList'][0]

        if self.exportType == 'pb':
            lastRLBookmark = self.pb.posts.recent(tag='.readinglist', count=1)
            last = lastRLBookmark['date']
        else:
            self.content = ''
            self.newcontent = ''
            # last = time.strptime((datetime.now() - timedelta(days = 1)).strftime('%c'))
            last = time.strptime("2013-01-01 00:00:00 UTC", '%Y-%m-%d %H:%M:%S UTC')

            if not os.path.exists(markdownFile):
                open(markdownFile, 'a').close()
            else:
                with open (markdownFile, 'r') as mdInput:
                    self.content = mdInput.read()
                    matchLast = re.search(re.compile('(?m)^Updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC)'), self.content)
                    if matchLast != None:
                        last = time.strptime(matchLast.group(1), '%Y-%m-%d %H:%M:%S UTC')

            last = datetime(*last[:6])

            rx = re.compile("(?m)^Updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC")
            self.content = re.sub(rx,'',self.content).strip()

        if 'Children' in readingList:
            cleanRx = re.compile("[\|\`\:_\*\n]")
            for item in readingList['Children']:
                if item['ReadingList']['DateAdded'] > last:
                    addtime = pytz.utc.localize(item['ReadingList']['DateAdded']).strftime('%c')
                    title = re.sub(cleanRx, ' ', item['URIDictionary']['title'].encode('utf8'))
                    title = re.sub(' +', ' ', title)
                    url = item['URLString']
                    description = ''

                    if 'PreviewText' in item['ReadingList']:
                        description = item['ReadingList']['PreviewText'].encode('utf8')
                        description = re.sub(cleanRx, ' ', description)
                        description = re.sub(' +', ' ', description)

                    if self.exportType == 'md':
                        self.itemToMarkdown(addtime, title, url, description)
                    else:
                        self.itemToPinboard(title, url, description)
                else:
                    break

        pluralized = 'bookmarks' if self.postedCount > 1 else 'bookmark'
        if self.exportType == 'pb':
            if self.postedCount > 0:
                sys.stdout.write('Added ' + str(self.postedCount) + ' new ' + pluralized + ' to Pinboard')
            else:
                sys.stdout.write('No new bookmarks found in Reading List')
        else:
            mdHandle = open(markdownFile, 'w')
            mdHandle.write('Updated: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC\n\n")
            mdHandle.write(self.newcontent + self.content)
            mdHandle.close()
            if self.postedCount > 0:
                sys.stdout.write('Added ' + str(self.postedCount) + ' new ' + pluralized + ' to ' + markdownFile)
            else:
                sys.stdout.write('No new bookmarks found in Reading List')

        sys.stdout.write("\n")

    def itemToMarkdown(self, addtime, title, url, description):
        self.newcontent += '- [' + title + '](' + url + ' "Added on ' + addtime + '")'
        if not description == '':
            self.newcontent += "\n\n    > " + description
        self.newcontent += "\n\n"
        self.postedCount += 1

    def itemToPinboard(self, title, url, description):
        suggestions = self.pb.posts.suggest(url=url)
        tags = suggestions[0]['popular']
        tags.append('.readinglist')

        self.pb.posts.add(url=url, description=title, \
                extended=description, tags=tags, shared=False, \
                toread=True)
        self.postedCount += 1

if __name__ == "__main__":
    exportTypes = []
    if len(sys.argv):
        for arg in sys.argv:
            if re.match("^(md|pb|all)$",arg) and exportTypes.count(arg) == 0:
                exportTypes.append(arg)
    else:
        exportTypes.append(DEFAULT_EXPORT_TYPE)

    for eType in exportTypes:
        _readingList(eType)

