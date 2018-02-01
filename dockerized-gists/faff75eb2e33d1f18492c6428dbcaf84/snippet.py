#!/usr/bin/python
'''
Google calendar CSV - https://support.google.com/calendar/answer/37118?hl=en&rd=2

1. make an abstractions google calendar 
2. customize this as needed
3. run this, redirecting to foo.csv
4. import as csv into google calendar

'''

import requests, sys

fmt = '"%s", %s, %s, %s, %s, %s, "%s", %s'

url = 'http://abstractions.io/api/schedule.json'

dates = { 'Thursday': '8/18/2016',
          'Friday': '8/19/2016',
          'Saturday': '8/20/2016' }

def get():
    r = requests.get(url)
    if r.status_code != 200:
        sys.exit("code %d for %s" % (r.status_code, url))
    return r.json()

def ampm(time):
    t = int(time)
    return "%02d:%02d %s" %( t / 100 % 12, t % 100, 'AM' if t < 1200 else 'PM')

print fmt % ('Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location')

for dayblob in get()['days']:
    day = dayblob['name']
    for stageblob in dayblob['stages']:
        stage = stageblob['name']
        for sessblob in stageblob['sessions']:
            who = sessblob['speaker']['name'].encode('ascii', 'ignore')
            what = sessblob['talk']['title'].encode('ascii', 'ignore')
            start = sessblob['time_start']
            end = sessblob['time_end']
            print fmt % (who, dates[day], ampm(start), dates[day], ampm(end), 'False', what, stage)

