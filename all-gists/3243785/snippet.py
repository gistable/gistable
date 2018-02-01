# wunder.py - vsergeev at gmail
# Simple command-line wunderground weather fetcher.
#
# Requires a wunderground API key (http://www.wunderground.com/weather/api,
# free sign-up).

import urllib, json, sys, os, tempfile
try:
	import fabulous.image
	image_render = True
except ImportError:
	image_render = False

# Wunderground API key
API_KEY = ""
# Location like zip code (60290), city (NY/New_York), auto by IP (autoip), ...
LOCATION = "02142"

# Fetch the subkey of a dictionary
def fetch_subkey(d, keylist):
	if keylist[0] not in d: return False
	return d[keylist[0]] if len(keylist) == 1 else fetch_subkey(d[keylist[0]], keylist[1:])

# Pretty-print child keys of a dictionary, under a path with a master title and
# child subtitles
def prettyprint_keys(d, title, path, child_keys):
	print title
	for k in child_keys:
		value = fetch_subkey(d, path + [k[1]])
		if value: print "\t%s: %s" % (k[0], value)

weather_json = urllib.urlopen("http://api.wunderground.com/api/%s/conditions/forecast/q/%s.json" % (API_KEY, LOCATION)).read()
weather_dict = json.loads(weather_json)

# Check for response->features->conditions and response->features->forecast
# success
if fetch_subkey(weather_dict, ['response', 'features', 'conditions']) != 1 or fetch_subkey(weather_dict, ['response', 'features', 'forecast']) != 1:
	print "Error fetching weather! Responses missing..."
	sys.exit(1)

# Cherry-pick and pretty-print some fields of the response

title = "Observation Location"
path = ["current_observation", "observation_location"]
child_keys = [ ("Name", "full"), ("Latitude", "latitude"), ("Longitude", "longitude"), ("Elevation", "elevation") ]
prettyprint_keys(weather_dict, title, path, child_keys)

print ""

title = "Current Weather"
path = ["current_observation"]
child_keys = [("Observation Time", "observation_time"), ("Local Time", "local_time"), ("Conditions", "weather"), ("Temperature", "temperature_string"), ("Relative Humidity", "relative_humidity"), ("Wind", "wind_string")]
prettyprint_keys(weather_dict, title, path, child_keys)

print ""

# "forecastday" key gives us an array of dictionaries, rather than another
# dictionary.
forecastday = fetch_subkey(weather_dict, ["forecast", "txt_forecast", "forecastday"])
print "Current Forecast"
print "\t%s:\t%s" % (fetch_subkey(forecastday[0], ['title']), fetch_subkey(forecastday[0], ['fcttext']))
print "\t%s:\t%s" % (fetch_subkey(forecastday[1], ['title']), fetch_subkey(forecastday[1], ['fcttext']))

print ""

# Render the current weather image with fabulous if it's available
if image_render:
	icon_url = fetch_subkey(weather_dict, ["current_observation", "icon_url"])
	if icon_url:
		tmp_fd, tmp_path = tempfile.mkstemp()
		tmp_f = os.fdopen(tmp_fd, 'w')
		tmp_f.write(urllib.urlopen(icon_url).read())
		tmp_f.flush()
		print fabulous.image.Image(tmp_path)
		tmp_f.close()
