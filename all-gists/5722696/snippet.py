#!/usr/bin/env python

"""
This script is designed to generate a simple HTML file with _all_ of your
Pinboard.in bookmarks.

You should edit the `username`, `password`, `bookmark_filename`, and `tag`
variables.

Requirements:

* requests
* dateutil
"""

import subprocess
import cgi
import time

import requests
from dateutil import parser as date_parser

# Your Pinboard username
username = ""

# The path where you'd like to store your HTML export
bookmark_filename = "/Users/dan/Dropbox/PinboardBookmarks.html"

# Your timezone
local_timezone = "America/Los_Angeles"

# (optional) A tag that you want to export by
tag = "programming"

# Your password
password = None

if not password:
    # Alternatively (if on OS X), use the Mac OS X keychain
    keychain_process = subprocess.Popen(["security", "find-internet-password", "-s", "pinboard.in", "-w"],
           stdout=subprocess.PIPE)
    trim_newlines = subprocess.Popen(["tr", "-d", "'\n'"],
           stdin=keychain_process.stdout,
           stdout=subprocess.PIPE)
    keychain_process.stdout.close()
    password, _ = trim_newlines.communicate()

BOOKMARK_FORMAT = u"""<DT><A HREF="{href}" ADD_DATE="{time}" PRIVATE="{private}" TOREAD="{toread}" TAGS="{tags}">{description}</a>\n"""
BOOKMARK_DESCRIPTION_FORMAT = u"""<DD>{extended}\n"""

def quote(text):
    return cgi.escape(text, quote=True).replace("\n", " ")

url = "https://api.pinboard.in/v1/user/api_token?format=json"
response = requests.get(url, auth=(username, password))
auth_token = "{}:{}".format(username, response.json()['result'])

if tag:
    url = "https://api.pinboard.in/v1/posts/all?format=json&tag={}&auth_token={}".format(tag, auth_token)
else:
    url = "https://api.pinboard.in/v1/posts/all?format=json&auth_token={}".format(auth_token)

response = requests.get(url)
with open(bookmark_filename, 'w') as bookmark_file:
    bookmark_file.write("""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Pinboard Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>""")

    for bookmark in response.json():
        bookmark['description'] = quote(bookmark['description'])
        bookmark['time'] = int(time.mktime(date_parser.parse(bookmark['time']).timetuple()))
        bookmark['private'] = 0 if bookmark['shared'] == 'yes' else 1
        bookmark['toread'] = 1 if bookmark['toread'] == 'yes' else 0

        tags = bookmark['tags'].split()
        if bookmark['toread'] == 1:
            tags.append('toread')

        bookmark['tags'] = ','.join(tags)
        bookmark_file.write(BOOKMARK_FORMAT.format(**bookmark).encode("utf-8"))

        if len(bookmark['extended']) > 0:
            bookmark['extended'] = quote(bookmark['extended'])
            bookmark_file.write(BOOKMARK_DESCRIPTION_FORMAT.format(**bookmark).encode("utf-8"))

        bookmark_file.write("\n")

    bookmark_file.write("""</DL></p>""")

