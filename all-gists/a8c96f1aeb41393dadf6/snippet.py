#! /usr/bin/env python
#-*- coding: utf-8 -*-

import json
import httplib2

from datetime import datetime
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

# Copy your credentials from the Google Developers Console
CLIENT_ID = 'XXXXXXXXXXXXXXXXXX.apps.googleusercontent.com'
CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXX'

# Check https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
# for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'

# DATA SOURCE
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"

# The ID is formatted like: "startTime-endTime" where startTime and endTime are
# 64 bit integers (epoch time with nanoseconds).
DATA_SET = "1051700038292387000-1451700038292387000"

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def retrieve_data():
    """
    Run through the OAuth flow and retrieve credentials.
    Returns a dataset (Users.dataSources.datasets):
    https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets
    """
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser:'
    print authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service.users().dataSources(). \
              datasets(). \
              get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET). \
              execute()

def nanoseconds(nanotime):
    """
    Convert epoch time with nanoseconds to human-readable.
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    # Point of entry in execution mode:
    dataset = retrieve_data()
    with open('dataset.txt', 'w') as outfile:
        json.dump(dataset, outfile)

    last_point = dataset["point"][-1]
    print "Start time:", nanoseconds(int(last_point.get("startTimeNanos", 0)))
    print "End time:", nanoseconds(int(last_point.get("endTimeNanos", 0)))
    print "Data type:", last_point.get("dataTypeName", None)
    print "Steps:", last_point["value"][0].get("intVal", None)