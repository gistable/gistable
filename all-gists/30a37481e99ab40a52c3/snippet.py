#!/usr/bin/env python

import requests
import os, sys

config = {
    'wootric_client_id': 'PUT CLIENT ID HERE',
    'wootric_client_secret': 'PUT CLIENT SECRET HERE'
}

form = dict(
    grant_type='client_credentials',
    client_id=config['wootric_client_id'],
    client_secret=config['wootric_client_secret']
)

resp = requests.post("https://api.wootric.com/oauth/token", data=form)

if resp.status_code != 200:
    print "Could not retrieve data from the server"
    sys.exit()

access_token = resp.json().get("access_token", None)

if not access_token:
    print "Access token not found"
    sys.exit()
    
print "Retreived access token: ", access_token