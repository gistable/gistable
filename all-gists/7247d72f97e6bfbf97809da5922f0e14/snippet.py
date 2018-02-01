
import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
import numpy as np
import urllib2 
from urlparse import urljoin
from bs4 import BeautifulSoup 
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import csv

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_p12_keyfile(
    service_account_email, key_file_location, scopes=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

def get_first_profile_id(service):
  # Declaring variable 
  profiles_list = []
  ua_list = []
  url_list = []

  # Accessing property 
  properties = service.management().webproperties().list(
    accountId='~all').execute()

  # Building property list
  for property in properties.get('items', []):
    ua_list.append(property.get('id'))

  #looping through ua list
  for ua in ua_list:
    profiles = service.management().profiles().list(
        accountId='XXXXXXX',
        webPropertyId= ua ).execute()

  # Building a list of Profile id
    for profile in profiles.get('items', []):
      profiles_list.append(profile.get('id'))

  # Loop through the profiles_list and get the best pages for each profile 
  for profile in profiles_list:
    response = service.data().ga().get(
      ids='ga:' + profile,
      start_date='1daysAgo',
      end_date='today',
      metrics='ga:sessions',
      dimensions='ga:pagePath',
      sort='-ga:sessions',
      filters='ga:sessions>400').execute()

    url_list.extend(row[0] for row in response.get('rows', []))

    #export in csv
    csv_out = open(response.get('profileInfo').get('profileName') + '.csv', 'wb')
    mywriter = csv.writer(csv_out)
    for row in url_list:
      mywriter.writerow([row])
    csv_out.close()

    #reset list
    url_list = []


def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Use the developer console and replace the values with your
  # service account email and relative location of your key file.
  service_account_email = 'email@projectnamehere.iam.gserviceaccount.com'
  key_file_location = 'yourkeyname.p12'

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location,
    service_account_email)
  profile = get_first_profile_id(service)

if __name__ == '__main__':
  main()