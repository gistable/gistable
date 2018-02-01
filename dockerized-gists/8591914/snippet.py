#coding: utf-8

import console
import keychain
import pickle

login = keychain.get_password('pinboard.in','pythonista')
if login is not None:
	user, pw = pickle.loads(login)
else:
	user, pw = console.login_alert('Pinboard Login', '')
	login = pickle.dumps((user, pw))
	keychain.set_password('pinboard.in', 'pythonista', login)
	
import requests
import json
pinboard_url = 'https://api.pinboard.in/v1/tags/get?format=json'
r = requests.get(pinboard_url, auth=(user, pw))
data = json.loads(r.text)
tags = data.items()

# minTags is the minimum amount of times this tag must link to a bookmark to be part of our final list.
# Change the value to 1 to grab all tags, for example.
minTags = 10
# This will generate a list without tags with less than minTags bookmarks.
filteredTags = [(str(k).lower(),int(v)) for k,v in tags if int(v) >= minTags]
# Change to True to sort your tags by name, otherwise they'll be sorted by count
sortByName = False

from operator import itemgetter

if sortByName:
	filteredTags = sorted(filteredTags, key=itemgetter(0))
else:
	filteredTags = sorted(filteredTags, key=itemgetter(1), reverse=True)

# finalTags kicks the conversion to a Launch Center Pro [list] converting each tag into tag=t:tag so we can use them to call Pinswift later.
finalTags = '|'.join([k for k,v in filteredTags])

title = 'Pick a Tag!'
label = 'Pick a Tag!'
description = 'Outcome for our Pythonista script to create a list with our most used tags from Pinboard ready to trigger at Pinswift'

# Comment the next line if you're not using Pinswift
action = 'pinswift:///u:%s/t:[list:%s|%s]' % (user, label, finalTags)

# Uncomment the next line if you're using Pushpin
#action = 'pushpin://feed?user=%s&tags=[list:%s|%s]' % (user, label, finalTags)

from urllib import quote
import webbrowser

import_lcp = 'launch://import?url=%s&title=%s&description=%s' % (quote(action), quote(title), quote(description))

webbrowser.open(import_lcp)
