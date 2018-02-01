#!/usr/bin/python

import urllib2
import json
import time
import calendar
import subprocess

url = 'http://api.thingm.com/blink1/events/01234567DEADC0DE'

last_time = 0

while True:
  req = urllib2.Request(url)
  res = urllib2.urlopen(req)
  data = res.read()

  ev = json.loads(data)

  if ev['event_count'] > 0:
    print 'events to process'
    for e in ev['events']:
      print e
      if int(e['date']) > last_time:
        print 'trigger: ' + e['name']
        subprocess.call(['./'+e['name']+'.sh'])

  last_time = calendar.timegm(time.gmtime())
  time.sleep(30)