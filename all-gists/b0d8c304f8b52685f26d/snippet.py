#!/usr/bin/env python

import base64
import json
import urllib2
import sys

sfurl = 'http://localhost:5138/identify/'

try:
  url = sfurl + base64.urlsafe_b64encode(sys.argv[1])
  response = urllib2.urlopen(url)
  j = json.load(response)
  if len(j['files'][0]['matches']) < 1:
    print >> sys.stderr, 'matching error: ' + j['files'][0]['errors']
    exit(1)
  if len(j['files'][0]['matches']) > 1:
    print >> sys.stderr, 'multiple matches: ' + ", ".join([x['puid'] for x in ['files'][0]['matches']])
    exit(1)
  match = j['files'][0]['matches'][0]['puid']
  if match == 'UNKNOWN':
    message = 'format unknown'
    if len(j['files'][0]['matches'][0]['warning']) > 0:
      message += ': ' + j['files'][0]['matches'][0]['warning']
    print >> sys.stderr, message
    exit(1)
  print match
except Exception as e:
  print >> sys.stderr, e
  exit(1)