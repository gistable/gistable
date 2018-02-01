'''
@author Michael J Bommarito II
@date Feb 26, 2011
@license Simplified BSD, (C) 2011.

This script demonstrates how to use Python to archive historical tweets.
'''

import codecs
import csv
import json
import os
import time
import urllib
import urllib2
import urlparse

# Set me to True if you want messages about what's going on.
DEBUG = True

def DEBUG(message):
	# Just a little debug macro.
	if DEBUG:
		print message

# Make sure we have parse_qs for <2.6, but prefer urlparse.
try:
	parse_qs = urlparse.parse_qs
except:
	import cgi
	parse_qs = cgi.parse_qs

def getLastMaxID(fileName):
	'''
	Read a tweet list to see what the last max_id should be.
	'''
	idList = []
	
	for line in codecs.open(fileName, 'r', 'utf8'):
		try:
			idList.append(int(line.split(',')[0].strip()))
		except:
			pass
	
	return min(idList)

def json2tuple(tweet):
	'''
	Convert a JSON dict to a tweet tuple.  If you want to include more or less data, this is where you can change it.
	'''
	# Clean up the geo field
	if tweet['geo'] == None:
		tweet['geo'] = ""
	elif tweet['geo']['type'] == 'Point':
		tweet['geo'] = ','.join(map(repr, tweet['geo']['coordinates']))
	
	# Clean up the text field
	tweet['text'] = tweet['text'].replace('"','""').replace("\r","").replace("\n","").replace("\t","")
	
	return ((tweet['id_str'],			# Tweet ID - DON'T REMOVE ME.
		tweet['from_user'],			# User handle
		tweet['geo'],				# Geostamp
		u'"{0}"'.format(tweet['created_at']),# Timestamp
		u'"{0}"'.format(tweet['text'])		# Tweet text content - what you see.		
		))

def doQuery(queryParameters):
	'''
	Execute a query and return the JSON results.
	'''
	queryURL = "http://search.twitter.com/search.json?" + urllib.urlencode(queryParameters)
	
	# We want to catch errors here to continue gracefully if possible.
	try:
		DEBUG("doQuery: Fetching {0}".format(queryURL))
		queryResponse = urllib2.urlopen(queryURL, timeout=10)		
	except urllib2.HTTPError, E:
		DEBUG("doQuery: Got an HTTP exception {0}".format(E.code))
			
		if E.code in [400, 420]:
			# 400, 420 => Slow down and be nice. Wait 10 minutes.
			time.sleep(600)		
		elif E.code == 503:
			# 503 => Twitter is getting hammered but it's not you, just wait 1 minute.
			time.sleep(60)
		else:
			# We should actually quit if it wasn't one of these.
			sys.exit(-1)

	return json.load(queryResponse, encoding="UTF-8")

def doSearch(term, resume = True, delay = 10):
	'''
	Run a search and download all historical data.
	'''
	# This is the basic query.
	queryParameters = dict(q=term,		# Search term
				rpp=100)	# Results per page
	
	
	# These are some state variables to keep track of what we're doing.
	nextPage = None
	maxID = None
	
	# Check to see if we should resume.
	fileName = "tweets_{0}.csv".format(term.translate(None, '?/\?%*:|"<>.'))
	if resume and os.path.exists(fileName):
		maxID = getLastMaxID(fileName)
	
	# Keep going until a condition within breaks.
	while True:
		if nextPage:
			'''
			This means we are currently paging through results.
			'''
			DEBUG("doSearch: nextPage")
			nextPageFields = parse_qs(nextPage)
			queryParameters['max_id'] = nextPageFields['max_id'].pop()
			if nextPageFields.has_key('?page'):
				queryParameters['page'] = nextPageFields['?page'].pop()
			else:
				if queryParameters.has_key('page'):
					del queryParameters['page']
		else:
			if maxID:
				'''
				This means we either just started downloading
				after resuming from file or that we need to start 
				the paging process over.
				'''
				DEBUG("doSearch: !nextPage, maxID={0}".format(maxID))
				queryParameters['max_id'] = maxID
			else:
				'''
				First time querying!
				'''
				DEBUG("doSearch: !nextPage, !maxID")
		
		print queryParameters
		jsonData = doQuery(queryParameters)
		
		# Set nextPage based on the response.
		if jsonData.has_key('next_page'):
			nextPage = jsonData['next_page']
		else:
			nextPage = None
			if queryParameters.has_key('max_id'):
				del queryParameters['max_id']
			
			if queryParameters.has_key('page'):
					del queryParameters['page']
		
		# Process and output the tweets
		tweets = map(json2tuple, jsonData['results'])
		
		tweetFile = codecs.open(fileName, 'a+', 'utf8')
		for tweet in tweets:
			tweetFile.write(','.join(tweet) + "\n")
		tweetFile.close()

		# Check to see if we've reached the end.
		if len(tweets) <= 1:
			DEBUG("len(tweets) = 1 => breaking.")
			break

		# Update maxID
		maxID = min([int(tweet[0]) for tweet in tweets])		
		
		# Sleep to be nice to Twitter.
		time.sleep(delay)

if __name__ == "__main__":
	doSearch("#python")