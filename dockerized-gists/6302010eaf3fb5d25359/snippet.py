#!/usr/bin/env python

"""
Quick script to beemind entering at least some meals into MyFitnessPal for the day.

Setup instructions:

  - install myfitnesspal, requests and keyring (if you don't have them)
  - call keyring.set_password("myfitnesspal", <your_username>, <your_password>)
  - call keyring.set_password("beeminder", <your_username>, <your_api_key>)

PROFIT!
"""

import datetime
import json
import keyring
import myfitnesspal
import requests
import urlparse

username = "katrielalex"
mfp_goal_name = "myfitnesspal"

BEEMINDER_URL = "https://www.beeminder.com/api/v1"
GET_URL       = BEEMINDER_URL + "/users/{username}/goals/{mfp_goal_name}.json".format(**locals())
POST_URL      = BEEMINDER_URL + "/users/{username}/goals/{mfp_goal_name}/datapoints.json".format(**locals())

# Set up a MFP API client
password = keyring.get_password("myfitnesspal", username)
client = myfitnesspal.Client(username, password)

# Look up the meals you entered today
today = datetime.date.today()
day = client.get_date(today.year, today.month, today.day)
entered = max(len(meal.entries) for meal in day.meals)

# Look up data points for today
api_key = keyring.get_password("beeminder", username)
result = json.loads(requests.get(GET_URL, data={"auth_token": api_key}).content)
updated_at = datetime.datetime.fromtimestamp(result["updated_at"])

# Do we need to log new data?
now = datetime.datetime.now()
today8am = now.replace(hour=8, minute=0, second=0)
if entered and updated_at < today8am:
    requests.post(POST_URL, data={
        "auth_token": api_key,
        "value": 1,
        "comment": "via myfitnesspal scripting on {}".format(now.isoformat())})
