#!/usr/bin/env python
__author__ = "m.busche@gmail.com"

# This program lets your blink1 device blink whenever Pi-hole has filtered ads
# Have fun.
# blink1 commandline tool: https://github.com/todbot/blink1/blob/master/docs/blink1-tool.md
# Pi-hole https://github.com/pi-hole/pi-hole

# To start this as a service I would recommend using supervisord

import json
import urllib2
import time
import os

blink1 = '/home/pi/blink1/commandline/blink1-tool'
piholeapiurl = 'http://localhost/admin/api.php'
interval = 15

def getPiholeAds():
	data = json.load(urllib2.urlopen(piholeapiurl))
	ads = data[u'ads_blocked_today']
	return ads
	
if __name__ == "__main__":
	os.popen(blink1 + ' --green --blink 2')
	oldvalue = int(getPiholeAds().replace(',',''))
	# print('Ads till now: ' + str(oldvalue))
	time.sleep(15)
	while 1:
		newvalue = int(getPiholeAds().replace(',',''))
		# print('Old value: ' + str(oldvalue))
		# print('New value: ' + str(newvalue))
		if newvalue > oldvalue:
			diff = str(newvalue - oldvalue)
			oldvalue = newvalue
			os.popen(blink1 + ' --red --blink ' + diff)
			
		time.sleep(interval)
	