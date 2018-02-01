#!/usr/bin/python

import os

import csv

reader = csv.DictReader(open('./instapaper-export.csv', 'rb'), delimiter = ',', quotechar = '"')
unread = []

for row in reader:
    if ( ( row['Folder'] != 'Archive' ) and ( row['Folder'] != 'Starred' ) ):
        unread.append(row['URL'])

for url in reversed(unread):
    print("Adding: " + url)
    os.system("""osascript -e 'tell application "Safari"' -e 'add reading list item \"""" + url + """"' -e 'end tell'""")