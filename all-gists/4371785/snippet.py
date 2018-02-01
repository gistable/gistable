#!/usr/bin/env python
import urllib
import pycurl
import sys
import json

from optparse import OptionParser

parser = OptionParser(usage="%prog: [options] [URL]")
parser.add_option('-p', '--projectid', help="Project ID")
parser.add_option('-u', '--user', help="User key")

(options, args) = parser.parse_args()
if not options.projectid:
   parser.print_help()
    sys.exit(1)
if not options.user:
    parser.print_help()
    sys.exit(1)

class Response:
    def __init__(self):
        self.response = {}
    def body_callback(self, buf):
        try:
            self.response = json.loads(buf)
        except:
            pass

def get_tasks(project_id, user_key):
    asana_url = 'https://app.asana.com/api/1.0/projects/%s/tasks' % project_id
    params = {'assignee': 'me'}
    try:
        t = Response()
        c = pycurl.Curl()
        c.setopt(c.URL, asana_url + '?' + urllib.urlencode(params))
        c.setopt(c.HTTPHEADER, ['Accept: application/json'])
        c.setopt(c.USERPWD, '%s:' % user_key)
        c.setopt(c.WRITEFUNCTION, t.body_callback)
        c.perform()
        c.close()
    except Exception as err:
        return -1
    finally:
        return t.response

print get_tasks(options.projectid, options.user)