'''
Go to https://code.google.com/apis/console/ and:
- create a new project, 
- enable access to the calendar api, 
- create a "service account" - that will give you an:
  * "email address" which is the service_account_name and
  * a private key that you need to save on you server
- go to the calendar and share it with the "email address" from above

Make sure your time is synchronized.

requirements are: google-api-python-client and pyOpenSSL
    pip install google-api-python-client pyOpenSSL
'''

import pprint
import pytz
from datetime import datetime, timedelta
import httplib2

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials


with open('privatekey.p12', 'rb') as f:
    key = f.read()

service_account_name = '...@developer.gserviceaccount.com'
calendarId = '...@group.calendar.google.com'

credentials = SignedJwtAssertionCredentials(
    service_account_name, key,
    scope=['https://www.googleapis.com/auth/calendar',
           'https://www.googleapis.com/auth/calendar.readonly'])

http = httplib2.Http()
http = credentials.authorize(http)

service = build(serviceName='calendar', version='v3', http=http)

lists = service.calendarList().list().execute()
pprint.pprint(lists)
print

# get events from calendar for the next 3 days
cest = pytz.timezone('Europe/Skopje')
now = datetime.now(tz=cest) # timezone?
timeMin = datetime(year=now.year, month=now.month, day=now.day, tzinfo=cest) + timedelta(days=1)
timeMin = timeMin.isoformat()
timeMax = datetime(year=now.year, month=now.month, day=now.day, tzinfo=cest) + timedelta(days=3)
timeMax = timeMax.isoformat()

events = service.events().list(calendarId=calendarId,
          timeMin=timeMin, timeMax=timeMax).execute()

pprint.pprint(events)
