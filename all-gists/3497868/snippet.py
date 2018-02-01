#!/usr/bin/env python

import urllib
import urlparse
import oauth2 as oauth
import json

consumer_key="consumer_key"
consumer_secret="consumer_secret"
access_token_url = 'https://www.tumblr.com/oauth/access_token'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)
client.add_credentials("email","password")
client.authorizations

params = {}
params["x_auth_username"] = "email"
params["x_auth_password"] = "passsword"
params["x_auth_mode"] = 'client_auth'

client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()
resp, token = client.request(access_token_url, method="POST",body=urllib.urlencode(params))

print resp
access_token = dict(urlparse.parse_qsl(token))

print access_token

access_token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
client = oauth.Client(consumer, access_token)
resp, user_data = client.request('http://api.tumblr.com/v2/user/info', method="POST")
user_data = json.loads(user_data)

print user_data