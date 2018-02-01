"""Reset admin password in Chef Server WebUI by removing admin user from DB"""

# based on http://lists.opscode.com/sympa/arc/chef/2011-08/msg00151.html

import urllib2
import json

COUCHSERV = 'localhost:5984'
COUCHDB = 'http://' + COUCHSERV + '/chef/'


userson = urllib2.urlopen(COUCHDB + '_design/users/_view/all').read()
users = json.loads(userson)

from pprint import pprint
#pprint(users)
#print json.dumps(users, sort_keys=True, indent=2)

for row in users['rows']:
  if row['key'] == u'admin':
    id = row['value']['_id']
    rev = row['value']['_rev']
    url = COUCHDB + id + '?rev=' + rev

    import httplib
    conn = httplib.HTTPConnection(COUCHSERV)
    conn.request('DELETE', url)

    print('Admin account removed. Restart Chef WebUI to recreate it with defaults.')
    print('For example: sudo service chef-server-webui restart')
    break
