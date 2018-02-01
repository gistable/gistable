#!/usr/bin/env python2
import sqlite3
import os
import sys
import webbrowser as wb
import urllib2

for path in (
        os.path.expanduser('~/.config/google-chrome/'),
        os.path.expanduser('~/.config/chromium/'),
        'C:\\Users\\%s\\AppData\\Local\\Google\\Chrome\\' % os.environ.get('USERNAME'),
        'C:\\Documents and Settings\\%s\\Local Settings\\Application Data\\Google\\Chrome\\' % os.environ.get('USERNAME')
        ):
    path += os.path.join('Default', 'History')
    if os.path.exists(path):
        break
else:
    print 'Chrome history file not found!'
    sys.exit()

conn = sqlite3.connect(path)
c = conn.cursor()

while True:
    c.execute('select * from urls order by RANDOM() limit 1;')
    url = c.fetchone()[1]
    
    try:
        urllib2.urlopen(url).read()
    except urllib2.URLError:
        pass
    else:
        wb.open(url)
        break
