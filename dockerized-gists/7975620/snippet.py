# http://stackoverflow.com/questions/20211990/sending-data-curl-json-in-python

import requests            #pip install requests
import simplejson as json  #pip install simplejson

url = "http://<ip-address>:3030"
widget = "welcome"
data = { "auth_token": "YOUR_AUTH_TOKEN", "text": "Python Greetings!!" }

fullUrl = "%s/widgets/%s" % (url, widget)
headers = {'Content-type': 'application/json'}
requests.post(fullUrl, data=json.dumps(data), headers=headers)