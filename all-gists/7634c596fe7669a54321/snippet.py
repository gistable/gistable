#!/usr/bin/env python

"""Sample Google Cloud Storage API client.

Based on <https://cloud.google.com/storage/docs/json_api/v1/json-api-python-samples>,
but removed parts that are not relevant to the Cloud Storage API.

Assumes the use of a service account, whose secrets are stored in
$HOME/google-api-secrets.json"""

import apiclient.discovery
import httplib2
import json
import oauth2client.client
import os

GOOGLE_API_SECRET_PATH = os.path.join(os.environ['HOME'], 'google-api-secrets.json')
BUCKET_NAME = 'my-bucket'

# Load secrets from file
google_api_secret = json.load(open(GOOGLE_API_SECRET_PATH))

# Make credentials object
credentials = oauth2client.client.SignedJwtAssertionCredentials(
    google_api_secret['client_email'],
    google_api_secret['private_key'],
    scope=['https://www.googleapis.com/auth/devstorage.read_write'])

# Make storage service object
storage = apiclient.discovery.build('storage', 'v1', http=credentials.authorize(httplib2.Http()))

# Get bucket object
req = storage.buckets().get(bucket=BUCKET_NAME)
resp = req.execute()
print json.dumps(resp)

# Make initial list request
req = storage.objects().list(
    bucket=BUCKET_NAME,
    fields='nextPageToken,items(name,size,contentType,metadata(my-key))')

# Submit list requests, handling paging
while req is not None:
  resp = req.execute()
  print json.dumps(resp)
  req = storage.objects().list_next(req, resp)