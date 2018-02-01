#!/usr/bin/env python

import cookielib
import json
import mechanize

#####
GOOGLE_USER = 'you@gmail.com'
GOOGLE_PASS = 'your-password'
#####

cookiejar = cookielib.LWPCookieJar()
browser = mechanize.Browser()
browser.set_cookiejar(cookiejar)

browser.open('http://ingress.com/intel')
for link in browser.links(url_regex='ServiceLogin'):
  browser.follow_link(link)

	browser.select_form(nr=0)
	browser.form['Email'] = GOOGLE_USER
	browser.form['Passwd'] = GOOGLE_PASS
	browser.submit()

	req = mechanize.Request('http://www.ingress.com/rpc/dashboard.getGameScore', 
		'{"method": "dashboard.getGameScore"}')

# 	req = mechanize.Request('http://www.ingress.com/rpc/dashboard.getThinnedEntitiesV2', '{\
#   "minLevelOfDetail": -1,\
#   "boundsParamsList": [\
#     {\
#       "id": "01202031112",\
#       "minLatE6": 52052490,\
#       "minLngE6": 10546875,\
#       "maxLatE6": 52268157,\
#       "maxLngE6": 10898438,\
#       "qk": "01202031112"\
#     },\
#     {\
#       "id": "01202031102",\
#       "minLatE6": 52052490,\
#       "minLngE6": 9843750,\
#       "maxLatE6": 52268157,\
#       "maxLngE6": 10195313,\
#       "qk": "01202031102"\
#     }\
#   ],\
#   "method": "dashboard.getThinnedEntitiesV2"\
# }')

# 	req = mechanize.Request('http://www.ingress.com/rpc/dashboard.getPaginatedPlextsV2', '{\
#   "desiredNumItems": 50,\
#   "minLatE6": 52146678,\
#   "minLngE6": 10138557,\
#   "maxLatE6": 52397517,\
#   "maxLngE6": 10917213,\
#   "minTimestampMs": -1,\
#   "maxTimestampMs": -1,\
#   "method": "dashboard.getPaginatedPlextsV2"\
# }')

	for cookie in cookiejar:
		if cookie.name == 'csrftoken':
			req.add_header('X-CSRFToken', cookie.value)
	cookiejar.add_cookie_header(req)

	jsonData = '\n'.join(mechanize.urlopen(req).readlines())
	print json.loads(jsonData)
  