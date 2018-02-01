#!/usr/bin/env python

# Looking for MP4 videos in infoq content.
#
# <div style="width: 320px; height: 265px; float: left; margin-right: 10px;">
#   <video poster="/styles/i/logo_scrubber.png" id="video" controls="controls" width="320" height="265">
#     <source src="http://d1snlc0orfrhj.cloudfront.net/presentations/12-mar-lockfreealgorithms.mp4" />
#   </video>
# </div>

import sys
import urllib2

from bs4 import BeautifulSoup

url = sys.argv[1]

request = urllib2.Request(url)

opener = urllib2.build_opener()

request.add_header('User-Agent', "Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10')")

html = opener.open(request).read()

soup = BeautifulSoup(html)

video_url = soup.find('video', id='video').source['src']

if (video_url):
    print video_url
    sys.exit(0)
else:
    sys.exit("failed to find video for " + url)
