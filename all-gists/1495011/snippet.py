#!/bin/env python
#
# Demo tool to generate the rtmpdump(1) command for streaming a song from Rdio.

import httplib
from optparse import OptionParser
from os.path import basename
from pprint import pprint
from pyamf.remoting.client import RemotingService
from rdioapi import Rdio
import sys
from urlparse import urlparse

# URL hosting the Flash player
FLASH_PLAYER_URL = 'http://www.rdio.com/api/swf'

# API endpoint for AMF
AMF_ENDPOINT = 'http://www.rdio.com/api/1/amf/'

# Exit with a message
def fail(msg):
    print >> sys.stderr, '%s: %s' % (basename(sys.argv[0]), msg)
    sys.exit(1)

# Recursively resolve the given URL, following 3xx redirects. Returns final URL
# that did not result in a redirect
def resolve_url(url):
    url = FLASH_PLAYER_URL
    while True:
        pr = urlparse(url)

        hc = httplib.HTTPConnection(pr.hostname)
        hc.request('GET', pr.path)
        hr = hc.getresponse()
        
        if hr.status / 100 == 3:
            url = hr.getheader('location')
        else:
            return url

op = OptionParser(
    usage='%prog [options] <key> <secret> <query>',
    description='''Emit an invocation of rtmpdump(1) that will fetch an FLV
file containing the audio to the first match of the given query to the Rdio
API.''')
opts, args = op.parse_args()

if len(args) < 3:
    op.error('missing required arguments')

key = args[0]
secret = args[1]
query = ' '.join(args[2:])

# Figure out the URL for the Flash player that we're going to 
# impersonate
flash_url = resolve_url(FLASH_PLAYER_URL)

# Create a REST API client
ra = Rdio(key, secret, {})

# Create an AMF API client
svc = RemotingService(AMF_ENDPOINT, referer=flash_url, amf_version=3)
svc.addHeader('Auth', chr(5))
rdio_svc = svc.getService('rdio')

# Search for the track to play
results = ra.search(query=query, types=','.join(['Track']),
    count=1)['results']
if not results:
    fail('no results found')

# Get a playback token
token = ra.getPlaybackToken(domain='std.in')

# Get playback information
#
# The end of the 'surl' value initially points to a 0:30 sample. Replace it to
# get the full track.
pi = rdio_svc.getPlaybackInfo({
    'domain': 'std.in',
    'playbackToken': token,
    'manualPlay': False,
    'playerName': 'api_544189',
    'type': 'flash',
    'key': results[0]['key']})
if not pi:
    fail('failed to get playback info')

auth = pi['auth']
surl = pi['surl'].replace('30s-96', 'full-192')

# Use rtmpdump(1) and ffmpeg(1) to grab the FLV file and then transcode it into
# an MP3
print 'rtmpdump ' \
        '-p "http://blog.std.in/" ' \
        '--app "ondemand?%s" ' \
        '-r "rtmpe://%s/ondemand/mp3:%s" ' \
        '-W "%s" | ' \
    'ffmpeg ' \
        '-f flv ' \
        '-i - ' \
        '-f mp3 ' \
        'foo.mp3' % (
    auth,
    'cp102543.edgefcs.net:1935',
    surl,
    flash_url)