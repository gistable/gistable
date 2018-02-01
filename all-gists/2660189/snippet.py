# Load Json into a Python object

import urllib2
import json
req = urllib2.Request("http://localhost:81/sensors/temperature.json")
opener = urllib2.build_opener()
f = opener.open(req)
json = json.loads(f.read())
print json
print json['unit']

# Array example

import urllib2
import json
req = urllib2.Request("http://vimeo.com/api/v2/video/38356.json")
opener = urllib2.build_opener()
f = opener.open(req)
json = json.loads(f.read())
print json
print json[0]['title']