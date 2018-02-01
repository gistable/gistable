#!/usr/bin/python

"""

Create a stage in your project, make it the last stage.
Make a task in the stage with this inline script:

#! /bin/bash

/some/path/bamboo-to-slack.py "${bamboo.planKey}" "${bamboo.buildPlanName}" "${bamboo.buildResultsUrl}"

Remember to make a channel with a Service Integration "Incoming WebHooks." The Slacker site will tell you the correct URL to put in the script below.

Requirements for this Python script: Requests (pip install requests, http://docs.python-requests.org/)

"""

import sys
import requests
import json

buildName = str(sys.argv[1])
jobName = str(sys.argv[2])
buildUrl = str(sys.argv[3])

buildStateUrl = 'http://YOUR_BAMBOO_URL/bamboo/rest/api/latest/result/{0}/latest.json?buildstate'.format(buildName)
r = requests.get(buildStateUrl)
buildState = r.json()['buildState']

if buildState != 'Successful':
  message = "Job \"{0}\" not successful! State: {1}. See {2}".format(jobName, buildState, buildUrl)
  payload = {'channel': '#YOUR_CHANNEL', 'username': 'Bamboo', 'text': message}
  r = requests.post('https://YOUR_COMPANY.slack.com/services/hooks/incoming-webhook?token=YOUR_TOKEN_HERE', data=json.dumps(payload))
  print "Slacker output: {0}".format(r.text)
