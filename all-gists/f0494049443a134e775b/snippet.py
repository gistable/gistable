import sys, csv, json, urllib2
from collections import OrderedDict

#
# Script to automate downloading and parsing data for all KFC restaurants in the UK.
#

__author__ = 'Lucas'
__homepage__ = 'http://www.flyingtophat.co.uk/'
__version__ = '1.0'
__date__ = '2014/05/08'

LOCATER_URL = "http://www.kfc.co.uk/our-restaurants/search?latitude={0}&longitude={1}&radius={2}&storeTypes="

JSON_ATTRIBUTES = OrderedDict([
    ("Store Name",   "storeName"),
    ("Post Code",    "postcode"),
    ("Phone Number", "telno"),
    ("Latitude",     "latitude" ),
    ("Longitude",    "longitude")
])

def extractValuesByKeys(keyValuePairs, keys):
    return [keyValuePairs[key] for key in keys]

def formatLocaterUrl(url, geolocation, radius):
    return url.format(geolocation[0], geolocation[1], radius)

def getJsonResponse(url):
    response = urllib2.urlopen(url)
    html = response.read()

    # Convert encoding
    html = html.decode("utf-8")
    html = html.encode("ascii", "ignore")

    return json.loads(html)

url = formatLocaterUrl(LOCATER_URL, [51.508515, -0.12548719999995228], 1000000)

stores = getJsonResponse(url)
storeRows = [extractValuesByKeys(store, JSON_ATTRIBUTES.values()) for store in stores]

csvWriter = csv.writer(sys.stdout)
csvWriter.writerow(JSON_ATTRIBUTES.keys())
csvWriter.writerows(storeRows)