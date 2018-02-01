# sample email header in JSON format
{ 'fromField': ['Deepak Jagdish', 'deepak.jagdish@gmail.com'],
  'toField': [['Daniel Smilkov', 'dsmilkov@gmail.com']],
  'dateField': 1372743719,
  'isSent': False,
  'threadid': '1439426117975266137',
}

import json

def filterEmails(emails):
  return [email for email in emails if email is not None and email['toField'] and email['fromField']]

f = open('allemails.json')
emails = filterEmails(json.load(f))

from collections import Counter
from datetime import datetime

def getSentRcvCounters(emails, year=None):
  sentCounter, rcvCounter = Counter(), Counter()
  for email in emails:
    if year and datetime.fromtimestamp(email['dateField']).year != year:
      continue
    if email['isSent']:
      for person in email['toField']:
        sentCounter[person[1]] += 1
    else:
      person = email['fromField']
      rcvCounter[person[1]] += 1
  return sentCounter, rcvCounter

def genMean(xx,p):
  mean = 0.0
  for x in xx:
    mean += x**p
  return (mean / len(xx))**(1.0/p)


def getTopcontacts(year=None):
  sentCounter, rcvCounter = getSentRcvCounters(emails, year)
  topcontacts = []
  for email in sentCounter:
    if sentCounter[email] > 0 and rcvCounter[email] > 0:
      topcontacts.append((email, genMean([sentCounter[email], rcvCounter[email]], -5)))
  topcontacts.sort(key=lambda x: x[1], reverse=True)
  return topcontacts

def getRank(topcontacts, email):
  for i, (contact, score) in enumerate(topcontacts):
    if contact == email:
      return i+1
      break
  return 0

results = [{'email': contact, 'ranks': []} for contact, score in getTopcontacts()[:10]]

for year in xrange(2005, 2014):
  topcontacts = getTopcontacts(year)
  for record in results:
    record['ranks'].append(getRank(topcontacts, record['email']))

print json.dumps(results)