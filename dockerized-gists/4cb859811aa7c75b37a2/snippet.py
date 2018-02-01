#!/usr/bin/python

import json
import requests

a = requests.get('http://wtfismyip.com/json')
b = json.loads(a.text)

isp = b['YourFuckingISP']
location = b['YourFuckingLocation']
hostname = b['YourFuckingHostname']
ip = b['YourFuckingIPAddress']

print ip + " [" + hostname + "] (" + isp + ")" + " <" + location + ">"
