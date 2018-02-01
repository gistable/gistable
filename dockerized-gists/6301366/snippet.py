#!/usr/bin/env python

import urllib2
import csv
import json
import boto

#Replace Google spreadsheet URL with your spreadsheet URL

url = "GOOGLE SPREADSHEET URL" + "&output=csv"
request = urllib2.Request(url)

cookie_handler = urllib2.HTTPCookieProcessor()
redirect_handler = urllib2.HTTPRedirectHandler()
opener = urllib2.build_opener(redirect_handler,cookie_handler)

u = opener.open(request)

print "Getting JSON"
data = csv.DictReader(u)
out = json.dumps([row for row in data])

print "Connecting to S3"
conn = boto.connect_s3()

#Replace 'my-bucket' with your bucket name

bucket = conn.get_bucket('my-bucket')

from boto.s3.key import Key

#Replace 'data.json' with your preferred file name

k = Key(bucket)
k.key = "data.json"
k.set_metadata("Cache-Control", "max-age=180")
k.set_metadata("Content-Type", "application/json")
k.set_contents_from_string(out)
k.set_acl("public-read")
print "Done, JSON is updated"