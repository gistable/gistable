# works only on Mac OS X with Evernote desktop client installed
# download the ohlife plaintext export and pipe it to this script
# eg. $ cat ~/Downloads/ohlife_2012blablabla.txt | python ohlife_to_evernote.py
# don't forget to change the notebook title if it's not "Journal"

from pipes import quote
import sys
import os

buf = ''
prevdate = ''
buf2 = []

def dateconvert(s):
    y = s[:4]
    m = s[5:7]
    d = s[8:10]
    return m + '/' + d + '/' + y

for line in sys.stdin.readlines():
    if line.startswith('2012'):
        buf2.append({'text': buf[1:-2], 'date': dateconvert(prevdate)})
        buf = ''
        prevdate = line[:10]
    else:
        buf += line.replace('\r\n', '\n')

for entry in buf2[1:]: # first is ''
    osa = 'tell application "Evernote" to create note with text "%s" title "%s" notebook "Journal" created (date "%s")' \
            % (entry['text'].replace('"', r'\"'),
               entry['date'], entry['date'])
    os.system("osascript -e %s" % quote(osa))
