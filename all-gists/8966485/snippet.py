import urllib.request
import urllib.parse
import json


__author__= 'adriano.mandala'

''''
Documentation from: https://developers.google.com/maps/documentation/geocoding/
Required parameters:
	address — The address that you want to geocode. 
	     or 
	latlng — The textual latitude/longitude value for which you wish to obtain the closest, human-readable address. See Reverse Geocoding for more information. 
	     or 
	components — A component filter for which you wish to obtain a geocode. See Component Filtering for more information. The components filter will also be accepted as an optional parameter if an address is provided.
	sensor — Indicates whether or not the geocoding request comes from a device with a location sensor. This value must be either true or false.
'''
params = urllib.parse.urlencode(
	{	
		'latlng': '38.1287373,13.3530497',
		'sensor': 'false'
	})
f = urllib.request.urlopen("http://maps.googleapis.com/maps/api/geocode/json?%s" % params)
a = json.loads(f.read().decode('utf-8'))

for result in a['results']:
	print(result['formatted_address'])
