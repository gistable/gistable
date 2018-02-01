# Quick intro to accessing Stubhub API with Python
# Ozzie Liu (ozzie@ozzieliu.com)
# Related blog post: http://ozzieliu.com/2016/06/21/scraping-ticket-data-with-stubhub-api/
# Updated 3/5/2017 for Python 3 and Stubhub's InventorySearchAPI - v2

import requests
import base64
import json
import pprint
import pandas as pd
import datetime

#### Step 1: # Obtaining StubHub User Access Token ####

## Enter user's API key, secret, and Stubhub login
app_token = input('Enter app token: ')
consumer_key = input('Enter consumer key: ')
consumer_secret = input('Enter consumer secret: ')
stubhub_username = input('Enter Stubhub username (email): ')
stubhub_password = input('Enter Stubhub password: ')

## Generating basic authorization token
combo = consumer_key + ':' + consumer_secret
basic_authorization_token = base64.b64encode(combo.encode('utf-8'))
# print(basic_authorization_token)

## POST parameters for API call
headers = {
        'Content-Type':'application/x-www-form-urlencoded',
        'Authorization':'Basic '+basic_authorization_token.decode('utf-8'),}
body = {
        'grant_type':'password',
        'username':stubhub_username,
        'password':stubhub_password,
        'scope':'PRODUCTION'}
## Making the call
url = 'https://api.stubhub.com/login'
r = requests.post(url, headers=headers, data=body)
token_respoonse = r.json()
access_token = token_respoonse['access_token']
user_GUID = r.headers['X-StubHub-User-GUID']

#### Step 2 - Searching inventory for an event ####
inventory_url = 'https://api.stubhub.com/search/inventory/v2'

headers['Authorization'] = 'Bearer ' + access_token
headers['Accept'] = 'application/json'
headers['Accept-Encoding'] = 'application/json'

## Enter event ID
eventid = '9837052'
data = {'eventid':eventid}

## GET request and change to Pandas dataframe
inventory = requests.get(inventory_url, headers=headers, params=data)
inv = inventory.json()

listing_df = pd.DataFrame(inv['listing'])

## Getting ticket prices out of the currentPice column of dicts - assuming they're all in USD
listing_df['amount'] = listing_df.apply(lambda x: x['currentPrice']['amount'], axis=1)

## Export to a csv file
listing_df.to_csv('tickets_listing.csv', index=False)

#### Step 3 - Adding Event and Venue Info ####

## Calling the eventsearch api
info_url = 'https://api.stubhub.com/catalog/events/v2/' + eventid
info = requests.get(info_url, headers=headers)

# pprint.pprint(info.json())

info_dict = info.json()
event_date = datetime.datetime.strptime(info_dict['eventDateLocal'][:10], '%Y-%m-%d')

event_name = info_dict['title']
event_date = info_dict['eventDateLocal'][:10]
venue = info_dict['venue']['name']

snapshot_date = datetime.datetime.today().strftime('%m/%d/%Y')

listing_df['snapshotDate'] = snapshot_date
listing_df['eventName'] = event_name
listing_df['eventDate'] = event_date
listing_df['venue'] = venue

my_col = ['snapshotDate','eventName','eventDate', 'venue', 'sectionName', 'row',
          'seatNumbers', 'quantity', 'deliveryTypeList', 'amount']

final_df = listing_df[my_col]

## Exporting final report
final_df.to_csv('tickets_listing_with_info.csv', index=False)
