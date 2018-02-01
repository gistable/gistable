#!/usr/bin/env python

import requests
import json
import StringIO
import datetime

hockeyToken = 'getyourowndamnkey'
appsEndpoint = 'https://rink.hockeyapp.net/api/2/apps'
crashesEndpoint = 'https://rink.hockeyapp.net/api/2/apps/%s/crashes/histogram?api_token=%s&format=json&start_date=%s&end_date=%s'

r = requests.get('%s?api_token=%s' % (appsEndpoint, hockeyToken))
responseJSON = r.json()

prodApps = []
devApps = []

for app in responseJSON['apps']:
  if app['release_type'] == 1:
		prodApps.append(app)
	else:
		devApps.append(app)

allCrashes = {}

for app in prodApps:
	appID = app['public_identifier']
	endDate = datetime.date.today()
	startDate = endDate - datetime.timedelta(30)
	crashesURL = crashesEndpoint % (appID, hockeyToken, startDate.isoformat(), endDate.isoformat())
	print('Requesting crashes for %s') % app['title']
	r = requests.get(crashesURL)

	crashesJSON = json.loads(r.text)

	for item in crashesJSON['histogram']:
		crashDate = item[0]
		crashValue = item[1]

		if allCrashes.has_key(crashDate):
			currentValue = int(allCrashes[crashDate])
			newValue = currentValue + crashValue
			allCrashes[crashDate] = newValue
		else:
			allCrashes[crashDate] = crashValue

graph = {"graph": {"title": "Production Crashes", "total": True, "type": "bar", "datasequences": [{"title": "Crashes", "color": "aqua", "datapoints": []}]}}
for key in sorted(allCrashes.iterkeys()):
	crashDate = datetime.datetime.strptime(key, '%Y-%m-%d').strftime('%m/%d')
	graph['graph']['datasequences'][0]['datapoints'].append({"title": crashDate, "value": allCrashes[key]})

jsonFile = open('crashes.json', 'w')
jsonFile.write(json.dumps(graph, sort_keys=True, indent=4))