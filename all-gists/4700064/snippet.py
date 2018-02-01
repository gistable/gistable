#!/usr/bin/env python
from urllib2 import urlopen, urlencode
from pymongo import connection
import json
from optparse import OptionParser
from time import sleep

verbose = 1

parser = OptionParser()
parser.add_option("-q", "--query", dest="query", type="string", action="store")
parser.add_option("-i", "--interval", dest="interval", type="int", action="store", default=10)
parser.add_option("-u", "--unique", dest="unique", action="store_true", default=False)
(options, args) = parser.parse_args()

params = {'q': options.query, 'type': 'tweet', 'window': 'a', 'perpage': '100'} # http://code.google.com/p/otterapi/wiki/Resources
if options.unique: params['nohidden']='0'
searchurl = "http://otter.topsy.com/search.json?"

c = connection.Connection()
db = c.topsy

def store(otterdata):
    if verbose: print otterdata['content'], otterdata['url'], otterdata['trackback_total']
    db.rawtopsy.save(otterdata)

count = 1

while count <= 10:
    queryurl = searchurl+urlencode(params)+'&page='+str(count)
    if verbose: print "* * * fetching ",queryurl
    data=urlopen(queryurl)
    resp=json.loads(data.read())
    if resp:
        for r in resp['response']['list']:
            store(r)
    count += 1
    sleep(options.interval)
