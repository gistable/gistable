import os
import urllib
import urllib2
import json
import pprint

# Grab credentials from the environment
consumer_key = os.environ['CLIENT_ID']
consumer_secret = os.environ['CLIENT_SECRET']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
login_server = os.environ['LOGIN_SERVER']

# Do OAuth username/password
token_url = login_server+'/services/oauth2/token'

params = urllib.urlencode({
  'grant_type': 'password',
  'client_id': consumer_key,
  'client_secret': consumer_secret,
  'username': username,
  'password': password
})

data = urllib2.urlopen(token_url, params).read()
oauth = json.loads(data)
pprint.pprint(oauth)

# Now do a query
params = urllib.urlencode({
  'q': 'SELECT Name FROM Account'
})

query_url = oauth['instance_url']+'/services/data/v23.0/query?%s' % params

headers = {
  'Authorization': 'OAuth '+oauth['access_token']
}

req = urllib2.Request(query_url, None, headers)
data = urllib2.urlopen(req).read()
result = json.loads(data)
pprint.pprint(result)