import requests
import json

urlbase = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
urlend = 'Zurich,Switzerland'

r = requests.get(urlbase+urlend) # request to google maps api

r=r.json()
if r.get('results'):
	for results in r.get('results'):
		latlong = results.get('geometry','').get('location','')
		latitude = latlong.get('lat','')
		longitude = latlong.get('lng','')
		break
	print latitude, longitude

else:
	print 'No results'