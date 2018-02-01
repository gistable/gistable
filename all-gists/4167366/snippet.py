import json, urllib2

CLIENT_IP = "xxxx"
CLIENT_ID = "xxxx"

def build_url(endpoint):
  return "http://{0}/api/{1}/{2}".format(CLIENT_IP, CLIENT_ID, endpoint)

def send(endpoint, value):
  url = build_url(endpoint)
  data = json.dumps(value)
	
  opener = urllib2.build_opener(urllib2.HTTPHandler)
  request = urllib2.Request(url, data=data)
  request.add_header('Content-Type', 'application/json')
  request.get_method = lambda: 'PUT'
  
  output = opener.open(request).read()
  return json.loads(output)


print(send("lights/3/state", {"bri": 0}))