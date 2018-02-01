# requirements
# biplist==0.6
# requests==2.1.0

import json

import requests

from biplist import readPlist
from requests.auth import HTTPBasicAuth
from StringIO import StringIO

username = ""
password = ""
auth = HTTPBasicAuth(username, password)

api_url = "https://api.path.com/3/"
method = "moment/feed"
args = ''

more = True
moments = []
old_oldest = 0

while more:
    r = requests.get(api_url+method+args, auth=auth)
    plist = readPlist(StringIO(r.content))

    if not plist or not plist['moments']:
        print "No more to add!"
        more = False

    else:
        oldest = plist['moments'][-1]['created']
        moments.extend(plist['moments'])

        # is there a better way to do this?
        f = open("moments.json", 'w')
        f.write(json.dumps(moments, sort_keys=True, indent=2))
        f.close()

        print "Wrote %s moments back to %s" % (len(moments), oldest)
        args = '?older_than=%s' % int(oldest)

        if old_oldest == oldest:
            more = False
        else:
            old_oldest = oldest

print "Done"