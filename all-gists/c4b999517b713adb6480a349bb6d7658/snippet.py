#!/usr/bin/env python

from google.cloud import monitoring

'''
# Using a service account with credentials in a json file:
JSON_CREDS = '/path/to/json'
from oauth2client.service_account import ServiceAccountCredentials
scopes  = ["https://www.googleapis.com/auth/monitoring",]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    JSON_CREDS, scopes)
'''

# From inside a GCE instance, with default account:
from oauth2client.contrib.gce import AppAssertionCredentials
credentials = AppAssertionCredentials([])

# 'project' is project ID, not name
myproject = 'main-shade-732'
client = monitoring.Client(project=myproject, credentials=credentials)

# Delete ALL custom metrics from this project.
all = client.list_metric_descriptors(type_prefix='custom.')
for a in all:
    descriptor = client.metric_descriptor(str(a.type))
    descriptor.delete()