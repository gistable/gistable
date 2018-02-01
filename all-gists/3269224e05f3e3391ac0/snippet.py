# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import hashlib
import hmac
import urllib2
import time
import json

import ast
import datetime
import calendar

#This code sample demonstrates a GET and a POST call to the Coinbase API
#Before implementation, set environmental variables with the names API_KEY and API_SECRET.

API_KEY = ""
API_SECRET = ""

base_uri = "https://coinbase.com/api/v1"

def make_request(url, body=None):
    opener = urllib2.build_opener()
    nonce = int(time.time() * 1e6)
    message = str(nonce) + url + ('' if body is None else body)
    signature = hmac.new(API_SECRET, message, hashlib.sha256).hexdigest()

    headers = {'ACCESS_KEY' : API_KEY,
             'ACCESS_SIGNATURE': signature,
             'ACCESS_NONCE': nonce,
             'Accept': 'application/json'}

    # If we are passing data, a POST request is made. Note that content_type is specified as json.
    if body:
        headers.update({'Content-Type': 'application/json'})
        req = urllib2.Request(url, data=body, headers=headers)
    # If body is nil, a GET request is made.
    else:
        req = urllib2.Request(url, headers=headers)

    try:
        return opener.open(req)
    except urllib2.HTTPError as e:
        print e
    return


# Get a UNIX Timestamp of 15 minutes into the future.
# See: https://coinbase.com/docs/api/authentication
future = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
expires = calendar.timegm(future.timetuple())

# Example of a GET request, where body is nil.
get_request = make_request('%s/account/balance?expire=%s' % (base_uri, expires))
try:
    balance_dict =  ast.literal_eval(get_request.readlines()[0])
    price = balance_dict['amount']
    print "Our current account balance: %sB⃦" % price
except:
    print "Error"

# Example of a POST request.

# Required parameters for POST /api/v1/buttons
button_params = {
    'button': {
        'name' : 'Equation of Time Cam Member',
        'price_string' : '2500.00',
        'price_currency_iso' : 'USD'
    }
}
#POST /api/v1/buttons
print make_request('%s/buttons?expire=%s' % (base_uri, expires), body=json.dumps(button_params)).read()