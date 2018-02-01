#!/usr/bin/python

import sys
import os
import requests
import json

url = 'http://api.forismatic.com/api/1.0/'

params = dict(
	method='getQuote',
	format='json',
	lang=sys.argv[1]
)

resp = requests.get(url=url, params=params)
data = json.loads(resp.text)

print data['quoteText'] + '.\n' + data['quoteAuthor']