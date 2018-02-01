#!/usr/bin/env python
import httplib2
import sys
import json
from urllib import urlencode
h = httplib2.Http(".cache")
print "Please hold while we retrive your IP address..."
r,ip = h.request("http://[fc72:6c3b:8c74:68a7:d8c3:b4e0:6cbd:9588]/ip/","GET")
url = "http://[fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535]/node/details/" + ip + "/save"
print "Looks like your IP is " + ip
print "All of the following questions are optional and publically visible. Most of them are displayed on the nodeinfo page about your node."
print "None of them are required"
headers = {"Referer":"http://[fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535]/node/details/" + ip + "/", "Origin":"http://[fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535]","Host":"fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535", "Content-type":"application/x-www-form-urlencoded"}
data = {}
data['is_submit'] = "1"
data['hostname'] = raw_input("What hostname would you like to use? ")
data['location'] = raw_input("Where is your node physically located? ")
data['os'] = raw_input("What operating system (and version) is your node running? ")
data['hardware'] = raw_input("What type of hardware is your node running on? ")
data['mx'] = raw_input("What node would you like to be your mail exchanger? ")
r,c = h.request(url,"POST",headers=headers, body=urlencode(data))
if r['status'] == "200":
    print c
    print "Saved. go to http://[fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535]/node/details/" + ip + " to see it live!"
else:
    print "wat. got status code " + r['status']