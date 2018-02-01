import json
import urllib
import urllib2
import time

""" Nike plus activity log
https://developer.nike.com

Output:
-- May --
Sun 05/26/13 : 5.59 miles 1:02:20 (11'10/mi)
Fri 05/24/13 : 4.01 miles 0:37:40 (9'24/mi)
Wed 05/22/13 : 6.17 miles 1:01:12 (9'55/mi)
"""

ACCESS_TOKEN = 'YOUR ACCESS TOKEN HERE'

base_url = 'https://api.nike.com'
url = '/me/sport/activities?access_token=%s' % ACCESS_TOKEN
headers = {'appid':'fuelband', 'Accept':'application/json'} # weird required headers, blah.
current_month = None

while url:

    req = urllib2.Request('%s%s' % (base_url, url), None, headers)
    r = urllib2.urlopen(req)
    resp = json.loads(r.read())
    r.close()

    if resp.get('data'):

        for activity in resp.get('data'):

            # 2013-05-26T14:48:42Z
            start_time = time.strptime(activity.get('startTime'), '%Y-%m-%dT%H:%M:%SZ')
            date = time.strftime('%a %m/%d/%y', start_time)

            month = time.strftime('%B', start_time)
            if month != current_month:
                current_month = month
                print ''
                print '--', current_month, '--'
            
            metrics = activity.get('metricSummary')

            # convert from km to mi and round
            miles = metrics.get('distance') * 0.621371
            distance = '%.2f' % round(miles, 2)

            # remove milliseconds
            duration = metrics.get('duration').partition('.')[0]

            pace = ''
            sp = duration.split(':')
            if (len(sp) == 3):
                duration_seconds = int(sp[0]) * 60 * 60 + int(sp[1]) * 60 + int(sp[2])
                seconds_per_mile = duration_seconds / miles
                hours, remainder = divmod(seconds_per_mile, 3600)
                minutes, seconds = divmod(remainder, 60)
                pace = '(%.0f\'%02.0f/mi)' % (minutes, seconds)

            print date, ':', distance, 'miles', duration, pace

        # pagination
        url = None 
        if resp.get('paging') and resp.get('paging').get('next'):
            url = resp.get('paging').get('next')    