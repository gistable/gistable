#
# python drive.py "origin" ["waypoint" ... ] "destination"
#
# i.e. python drive.py "Union Square, San Francisco" "Ferry Building, San Francisco" 'Bay Bridge' SFO

import sys, json, urllib2, md5, os.path, pprint
from math import radians, sin, cos, atan2, pow, sqrt
from urllib import quote_plus
from xml.sax.saxutils import escape
from optparse import OptionParser

parser = OptionParser("Usage: %prog [options] origin [waypoint ...] destination")
parser.add_option(
	"--cache",
	dest="cache",
	help="cache the result of query for Google into DIR",
	metavar="DIR")

(options, args) = parser.parse_args()

if len(args) < 2:
	parser.error("incorrect number of arguments")

def urlForDirection(args):
	origin = args[0]
	destination = args[-1]

	url = "http://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&sensor=false"
	url = url % (quote_plus(origin), quote_plus(destination))

	if len(args) > 2:
		url += '&waypoints=' + quote_plus('|'.join(args[1:-1]))

	return url

def cachePath(url):
	return options.cache + '/' + md5.new(url).hexdigest() + '.drive'


def fetchDirection(url):
	data = None
	cache_path = None
	fetched = False

	if options.cache:
		cache_path = cachePath(url)
		if os.path.isfile(cache_path):
			with file(cache_path, 'r') as fp:
				data = json.load(fp)

	if not data:
		fp = urllib2.urlopen(url)
		data = json.load(fp)
		fp.close()
		fetched = True

	if options.cache and fetched:
		fp = file(cache_path, 'w')
		json.dump(data, fp)
		fp.close()

	if data.get('status') != 'OK':
		error('Bad data')

	route = data['routes'][0]
	return route['legs']

def namedWaypoint(coordinate, name):
	print '\t<wpt lat="%(lat).6f" lon="%(lng).6f">' % coordinate
	print '\t\t<name>%s</name>' % escape(name.encode('utf-8'))
	print '\t</wpt>'

def waypoint(coordinate):
	print '\t<wpt lat="%(lat).6f" lon="%(lng).6f"/>' % coordinate

def decodePoly(pts):
	step1 = [ord(x) - 63 for x in pts]

	step2, vals = [], []
	for val in step1:
		vals.insert(0, val & 0x1f)
		if val < 0x20:
			val = 0
			for n in vals:
				val = (val << 5) + n
			if val % 2: val = ~(val - 1)
			val /= 2.0
			val /= 100000.0

			step2.append(val)
			vals = []

	step3 = []
	for lat, lng in zip(step2[0::2], step2[1::2]):
		if len(step3) > 0:
			lat += step3[-1]['lat']
			lng += step3[-1]['lng']
		step3.append({'lat':lat, 'lng':lng})

	return step3

def distanceBetweenPoints(a, b):
	lat1 = radians(a['lat'])
	lng1 = radians(a['lng'])
	lat2 = radians(b['lat'])
	lng2 = radians(b['lng'])

	R = 6371.0 * 1000 # radius of earth by km

	a = pow(sin((lat1 - lat2) / 2.0), 2) + pow(sin((lng1 - lng2) / 2.0), 2) * cos(lat1) * cos(lat2)

	c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))

	return R * c # / 1.6 * 5280.0 # to mile, then to feet

def complementPoints(points, duration, distance):
	result = []

	for a, b in zip(points[0:-1], points[1:]):
		dd = distanceBetweenPoints(a, b)
		dt = duration * (dd / distance)

		t = 0.0
		lat = b['lat'] - a['lat']
		lng = b['lng'] - a['lng']
		while t < dt:
			r = t / dt
			pt = {'lat': a['lat'] + lat * r, 'lng': a['lng'] + lng * r}
			result.append(pt)
			t += 5

	result.append(points[-1])

	return result

def printGPX(legs):
	print '<?xml version="1.0"?>'
	print '<gpx version="1.1" creator="drive.py coded by basuke">'

	namedWaypoint(legs[0]['start_location'], legs[0]['start_address'])

	for leg in legs:
		for step in leg['steps']:
			start = step['start_location']
			end = step['end_location']
			duration = step['duration']['value']
			distance = step['distance']['value']

			decodePoly(step['polyline']['points'])
			points = decodePoly(step['polyline']['points'])
			points.insert(0, start)
			points.append(end)

			points = complementPoints(points, duration, distance)
			for pt in points:
				waypoint(pt)

		namedWaypoint(leg['end_location'], leg['end_address'])

	print '</gpx>'

url = urlForDirection(args)
legs = fetchDirection(url)
printGPX(legs)
