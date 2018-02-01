# -*- coding: utf-8 -*-

import re, urllib2, json


def countable_noun(thing):
	'''
	searches Google NGram to see if a word is a countable/mass noun
	returns True if countable, False if not

	ex: cats are countable (many cats)
	    bread is not (much bread)
	'''

	# format into url (replace spaces with + for url)
	thing = re.sub(' ', '\+', thing)
	url = 'https://books.google.com/ngrams/graph?content=many+' + thing + '%2C+much+' + thing + '&year_start=1800&year_end=2000'
	response = urllib2.urlopen(url)
	html = response.read()

	# extract timeseries data from html source
	# if an error thrown, it's likely there's no match for the term
	thing = re.sub('\+', ' ', thing)
	try:
		many_data = json.loads(re.search('\{"ngram": "many ' + thing + '".*?\}', html, re.IGNORECASE).group(0))['timeseries']
		many = sum(many_data) / float(len(many_data))
	except:
		many = 0.0

	try:
		much_data = json.loads(re.search('\{"ngram": "much ' + thing + '".*?\}', html, re.IGNORECASE).group(0))['timeseries']
		much = sum(much_data) / float(len(much_data))
	except:
		much = 0.0

	# return True if countable; False if not
	if many > much:
		return True
	return False
