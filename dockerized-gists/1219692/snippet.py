#!/usr/bin/env python
"""
This script looks up how many followers two different Twitter accounts do have in common.

Usage:

    twitter_follower_intersect.py username username

You'll need Python and the Python Twitter Tools to get this running.

    http://pypi.python.org/pypi/twitter/

Also you will have to create an app at https://dev.twitter.com/apps/
and enter your credentials below:
"""

auth_token = '...'
auth_token_secret = '...'
consumer_key = '...'
consumer_secret = '...'

from twitter import Twitter, OAuth
import sys, os

if len(sys.argv) != 3:
	print 'Usage:\n\n'+os.path.basename(sys.argv[0])+' screenname1 screenname2';

t = Twitter(auth=OAuth(auth_token, auth_token_secret, consumer_key, consumer_secret))

user_a = sys.argv[1]
user_b = sys.argv[2]

a = t.followers.ids(user=user_a)
b = t.followers.ids(user=user_b)
c = []

for id in a:
	try:
		b.index(id)
		c.append(id)
	except:
		True
	
print '\n'+user_a, 'has', len(a), 'follower'
print user_b, 'has', len(b), 'follower'
print user_a, 'and', user_b, 'have', len(c), 'followers in common'

if len(c) > 100: 
	c = c[:100]
	print '\nfirst 100 common followers are:'
elif len(c) > 0:
	print '\nthese are the common followers:'
	
if len(c) > 0:
	common_info = t.users.lookup(user_id=','.join(map(str, c)))
	common = []
	for u in common_info: 
		common.append(u['screen_name'])
		
	print ', '.join(common)
	
print