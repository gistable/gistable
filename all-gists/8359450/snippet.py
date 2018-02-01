#!/usr/bin/python
"""
Script to fetch SPOT url and: 1) save lat,lon coordinates to a file, 2) save all spot messages as JSON, 3) and xml as well.
Files get re-written on every run, if there's new data. Oh, it writes to stderr if batteryState isn't GOOD - so if you run from cron, you'll get email when your spot batteries need to be changed.
"""
import urllib2
import json
import sys

""" Edit these items: """
#spot_id = "0Vn4kA4MiPgNSYD52NgPjuVJDpUCSUlGW"
spot_id = "0W8hq7UcGlKSuEszhPnJXzPMTlgRJgFhP"
last_latlon_cache = "/home/charlie/lastspotlocation.txt"
json_cache = "/home/charlie/spotlocations.json"
xml_cache = "/home/charlie/spotlocations.xml"

url = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/%s/message" % spot_id

try:
    response = urllib2.urlopen(url)
    data = json.load(response)
    xml_response = urllib2.urlopen(url + ".xml").read()
except Exception, err:
    # the API isn't always reliable.. exit silently
    sys.stdout.write("ERROR retreiving URL: %s" % err)
    sys.exit(1)

if 'errors' in data.get('response', {}):
    sys.stdout.write(str(data['response']['errors']))
    sys.exit(0)
else:
    try:
        data = data['response']['feedMessageResponse']
    except KeyError:
        sys.stderr.write("ERROR: JSON received from URL contains no feedMessageResponse,"
                         " but response->errors wasn't populated. WAT.")
        sys.exit(0)

    count = int(data.get('count', 0))
    if count == 0:
        sys.stdout.write("0 locations found?!\n%s" % data)
        sys.exit(0)

    last_message = data.get('messages', {}).get('message', {})[0]

    # write to stderr (so you get cron mail) if batteryState is not GOOD.
    if 'GOOD' not in last_message.get('batteryState', 'GOOD'):
        sys.stderr.write("WARNING: spot battery is in state: %s" % last_message.get('batteryState'))

    # write the last lat,lon to a file:
    fh = open(last_latlon_cache, 'w')
    fh.write("%s,%s" % (last_message.get('latitude', 0), last_message.get('longitude', 0)))
    fh.close()

    # write all messages return from spot API as json:
    fh = open(json_cache, 'w')
    fh.write(str(data.get('messages', {}).get('message', {})))
    fh.close()

    # write all messages return from spot API as XML:
    fh = open(xml_cache, 'w')
    fh.write(str(xml_response))
    fh.close()
