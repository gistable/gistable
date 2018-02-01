#! /usr/bin/env python

import hashlib
import urllib
import time
try:
	import simplejson as json
except ImportError:
	import json
from pprint import pprint
import getpass

current_user = getpass.getuser()

class Mixpanel(object):

	ENDPOINT = 'http://mixpanel.com/api/2.0'

	def __init__(self, api_key, api_secret):
		self.api_key = api_key
		self.api_secret = api_secret
		
	def request(self, method, params, request=True):
		"""
			methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
					  will give us http://mixpanel.com/api/2.0/events/properties/values/
			params - Extra parameters associated with method
		"""
		params['api_key'] = self.api_key
		params['expire'] = int(time.time()) + 600   # Grant this request 10 minutes.
		if 'sig' in params: del params['sig']
		params['sig'] = self.hash_args(params)

		request_url = '%s/%s?%s' % (self.ENDPOINT, method, self.unicode_urlencode(params))

		print request_url
		if request:
			request = urllib.urlopen(request_url)
			data = request.read()
			return data

	def unicode_urlencode(self, params):
		"""
			Convert lists to JSON encoded strings, and correctly handle any 
			unicode URL parameters.
		"""
		if isinstance(params, dict):
			params = params.items()
		for i, param in enumerate(params):
			if isinstance(param[1], list): 
				params[i] = (param[0], json.dumps(param[1]),)

		return urllib.urlencode(
			[(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params]
		)

	def hash_args(self, args, secret=None):
		"""
			Hashes arguments by joining key=value pairs, appending a secret, and 
			then taking the MD5 hex digest.
		"""
		for a in args:
			if isinstance(args[a], list): args[a] = json.dumps(args[a])

		sorted_args = sorted(args.keys())
		if 'callback' in sorted_args:
			sorted_args.remove('callback')
		args_joined = ''.join([
			'%s=%s' % (isinstance(x, unicode) and x.encode("utf-8") or \
			x, isinstance(args[x], unicode) and \
			args[x].encode("utf-8") or args[x]) for x in sorted_args
		])
		hash = hashlib.md5(args_joined)

		if secret:
			hash.update(secret)
		elif self.api_secret:
			hash.update(self.api_secret)
		return hash.hexdigest() 

def engage(properties, params={}):
	import base64, urllib2
	data = base64.b64encode(json.dumps(properties))
	host = 'api.mixpanel.com'
	endpoint = 'engage'
	params['data'] = data
	request = 'http://%s/%s/?%s' % (host, endpoint, urllib.urlencode(params))
	print request
	print urllib2.urlopen(request).read()

if __name__ == '__main__':
	api_key = "YOUR_DEFAULT"
	api_secret = "YOUR_DEFAULT"
	token = "YOUR_DEFAULT"
	
	#Welcome the user and ask for details
	print "Welome. This Script will all the users in a project."
	print "This is for real. You've been warned, " + current_user + "."
	input_keys = raw_input("Would you like to input custom api key/token? y/(n)")
	if input_keys == 'y':
		api_key = raw_input("Please paste in the project's' API key:")
		api_secret = raw_input("Please paste in the project's' API secret:")
		token =  raw_input("Please paste in the project's' token:")
		
	api = Mixpanel(
	api_key = api_key, #your api key and secret.
	api_secret = api_secret,
	)
	params = {
	}
	
	response = api.request('engage', params, True)
	data = json.loads(response)['results']
	while len(data) > 0:
		response = api.request('engage', params, True)
		data = json.loads(response)['results']
		for user in data:
			print "deleting: " + user['$distinct_id']
			distinct_id = user['$distinct_id']
			engage({
					'$token': token,
					'$distinct_id': distinct_id,
					'$delete': True,
				})

