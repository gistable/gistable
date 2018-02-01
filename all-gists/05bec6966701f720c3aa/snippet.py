#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple intro to using the Google Analytics API v3.

This application demonstrates how to use the python client library to access
Google Analytics data. The sample traverses the Management API to obtain the
authorized user's first profile ID. Then the sample uses this ID to
contstruct a Core Reporting API query to return the top 25 organic search
terms.

Before you begin, you must sigup for a new project in the Google APIs console:
https://code.google.com/apis/console

Then register the project to use OAuth2.0 for installed applications.

Finally you will need to add the client id, client secret, and redirect URL
into the client_secrets.json file that is in the same directory as this sample.

Sample Usage:

  $ python hello_analytics_api_v3.py

Also you can also get help on all the command-line flags the program
understands by running:

  $ python hello_analytics_api_v3.py --help
"""

__author__ = 'api.nickm@gmail.com (Nick Mihailovski)'


import argparse
import sys
import csv
import string

from apiclient.errors import HttpError
from apiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

class SampledDataError(Exception): pass


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__,
      scope='https://www.googleapis.com/auth/analytics.readonly')

  # Try to make a request to the API. Print the results or handle errors.
  try:
    profile_id = profile_ids[profile]
    if not profile_id:
      print 'Could not find a valid profile for this user.'
    else:
      for start_date, end_date in date_ranges:
        limit = ga_query(service, profile_id, 0,
                                 start_date, end_date).get('totalResults')
        for pag_index in xrange(0, limit, 10000):
          results = ga_query(service, profile_id, pag_index,
                                     start_date, end_date)
          if results.get('containsSampledData'):
            
            raise SampledDataError
          print_results(results, profile_id, pag_index, start_date, end_date)

  except TypeError, error:    
    # Handle errors in constructing a query.
    print ('There was an error in constructing your query : %s' % error)

  except HttpError, error:
    # Handle API errors.
    print ('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason()))

  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')
  
  except SampledDataError:
    # force an error if ever a query returns data that is sampled!
    print ('Error: Query contains sampled data!')


def ga_query(service, profile_id, pag_index, start_date, end_date):

  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_date,
      end_date=end_date,
      metrics='ga:pageviews',
      dimensions='ga:date,ga:landingPagePath,ga:sourceMedium,ga:networkLocation,ga:country,ga:region,ga:city',
      sort='-ga:pageviews',
      samplingLevel='HIGHER_PRECISION',
      start_index=str(pag_index+1),
      max_results=str(pag_index+10000)).execute()
      

def print_results(results, profile_id, pag_index, start_date, end_date):
  """Prints out the results.

  This prints out the profile name, the column headers, and all the rows of
  data.

  Args:
    results: The response returned from the Core Reporting API.
  """

  # New write header
  global write_headers, first_headers
  if pag_index == 0 and (start_date, end_date) == date_ranges[0]:
    print 'Profile Name: %s' % results.get('profileInfo').get('profileName')
    columnHeaders = results.get('columnHeaders')
    cleanHeaders = [str(h['name']) for h in columnHeaders]
    cleanHeaders.insert(0, 'profile_id')
    if write_headers:
      writer.writerow(cleanHeaders)
      write_headers = False
      first_headers = cleanHeaders
    else:
      assert cleanHeaders == first_headers
  print 'Now pulling data from %s to %s.' %(start_date, end_date)



  # Print data table.
  if results.get('rows', []):
    for row in results.get('rows'):
      for i in range(len(row)):
        old, new = row[i], str()
        for char in old:
          new += char if char in string.printable else ''
        row[i] = new
      row.insert(0, profile_id)
      writer.writerow(row)

  else:
    print 'No Rows Found'

  limit = results.get('totalResults')
  print pag_index, 'of about', int(round(limit, -4)), 'rows.'
  return None


profile_ids = profile_ids = {'My Profile 1':  '1234',
##                             'My Profile 2':  '1234567',
##			     'My Profile 3':  '1234567',
                           'My Profile 4':  '5678'}

# Uncomment this line & replace with 'profile name': 'id' to query a single profile
# Delete or comment out this line to loop over multiple profiles.

##profile_ids = {'ryanpraski':  '123456789'}


date_ranges = [('2015-08-01',
               '2016-02-08')]#,
               #('2015-09-01',
              # '2015-09-30'),
              # ('2015-10-01',
              # '2015-10-31'),
              # ('2015-11-01',
              #  '2015-11-30'),
              # ('2015-12-01',
              # '2015-12-22')]

path = 'C:\\Users\\ryanpraski\\Documents\\Google Analytics Python Data\\' #replace with path to your folder where csv file with data will be written
filename = 'google_analytics_data_2.csv' #replace with your filename.
f = open(path + filename, 'wt')
writer = csv.writer(f, lineterminator='\n')
write_headers = True
first_headers = []

for profile in sorted(profile_ids):
  if __name__ == '__main__': main(sys.argv)
  print "Profile done. Next profile..."

f.close()
print "All profiles done."

