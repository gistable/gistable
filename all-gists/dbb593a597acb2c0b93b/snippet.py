#!/usr/bin/python

import bluetooth
import time
import requests
from requests.exceptions import ConnectionError

payload =''

while True:
    print "Checking " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    result = bluetooth.lookup_name('78:7F:70:38:51:1B', timeout=5)
	
    if (result != None and payload!='ON'):
        print "User present"
	payload ='ON'
	try:
		r = requests.put("http://localhost:8080/rest/items/JamesInOffice/state",data=payload)
	except ConnectionError as e:
		print e
		r = "No Response"
		payload = ''
    elif (payload != 'OFF' and result == None):
        print "User out of range"
	payload ='OFF'
	try:
		r = requests.put("http://localhost:8080/rest/items/JamesInOffice/state",data=payload)
	except ConnectionError as e:
		print e
		r = "No Response"
		payload = ''
    time.sleep(10)