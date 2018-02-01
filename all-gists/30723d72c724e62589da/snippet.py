#!/usr/bin/env python

import urllib2
import json
import os
from datetime import datetime
import re


params = {
	'access_token': '' #write down access token here
}

username_or_id = raw_input('Username or ID: ')

try:
	uid = int(username_or_id)
except ValueError:
	uid = json.loads(urllib2.urlopen('http://graph.facebook.com/%s' % username_or_id).read())['id']

le_url = "https://graph.facebook.com/v2.3/%s/photos?access_token=%s&fields=images&type=uploaded" % (uid, params['access_token'])

folder_location = raw_input('Where to save these: ')
if(os.path.isdir(folder_location) != True):
	os.mkdir(folder_location)

def fetch_image_from_url(url):
	api_response = json.loads(urllib2.urlopen(url).read())
	for i in range(0, api_response['data'].__len__()):
		img_url = api_response['data'][i]['images'][0]['source']
		fdata = urllib2.urlopen(img_url).read()
		file_name = re.search('^(.*)\?.*$', os.path.split(img_url)[-1]).group(1)
		outfile = open(os.path.join(folder_location, file_name), 'wb')
		outfile.write(fdata)
		outfile.close()

	try:
		if(api_response['paging']['next']):
			fetch_image_from_url(api_response['paging']['next'])
	except:
		pass

startTime = datetime.now()
fetch_image_from_url(le_url)
print "Done! Total time %ss." % (datetime.now() - startTime).seconds