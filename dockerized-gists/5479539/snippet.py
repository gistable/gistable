#!/usr/bin/python2

import logging
import sys
import couchdb
import json
from libgreader import GoogleReader, ClientAuthMethod, Feed

"""
Original can be obtained here: https://gist.github.com/Nazgolze/5479539
Released to the public domain.
"""

db_name = "YOUR DB NAME GOES HERE"
username = "YOUR USERNAME GOES HERE"
password = "YOUR PASSWORD GOES HERE"

def loadUntilSuccessful(subscription, load):
  try:
    subscription.loadItems(loadLimit=load)
  except Exception:
    logging.warning(sys.exc_info()[0])
    print "Continuing..."
    sys.exc_clear()
    loadUntilSuccessful(subscription, load)

def loadMoreUntilSuccessful(subscription, load):
  try:
    subscription.items = []
    subscription.itemsById = {}
    subscription.loadMoreItems(loadLimit=load)
  except Exception:
    logging.warning(sys.exc_info()[0])
    print "Continuing..."
    sys.exc_clear()
    loadMoreUntilSuccessful(subscription, load)

couch = couchdb.Server('http://localhost:5984')
try:
  db = couch[db_name]
except Exception:
  db = couch.create(db_name)
auth = ClientAuthMethod(username, password)
reader = GoogleReader(auth)
ll = 100
reader.buildSubscriptionList()
l = reader.getSubscriptionList()

for li in l:
  print li.title.encode('ascii', 'xmlcharrefreplace')
  loadUntilSuccessful(li, ll)
  while li.lastLoadLength > 0:
    bulk_upload = []
    for i in li.getItems():
      doc = {}
      doc = i.data
      if len(li.categories) > 0:
        doc["label"] = li.categories[0].label
      bulk_upload.append(doc)
    db.update(bulk_upload)
    loadMoreUntilSuccessful(li, ll)
