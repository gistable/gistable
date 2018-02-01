#!/usr/bin/env python3

import simplekml
import urllib.request
try:
    import simplejson as json
except ImportError:
    import json

fr24_flight_code = ""
output_file = ""
api_url = "http://krk.fr24.com/_external/planedata_json.1.3.php?f={0}".format(fr24_flight_code)

kml = simplekml.Kml()
html = urllib.request.urlopen(api_url)
flight = json.loads(html.read().decode('utf-8'))
trail = flight["trail"]
temp_path = [trail[x:x+3] for x in range(0, len(trail), 3)]
# Rearrange lat/long and format as tuple
path = [(x[1], x[0], x[2]*3.048) for x in reversed(temp_path)]
flight_path = kml.newlinestring(
                name=fr24_flight_code,
                description="Flight path of {0}".format(fr24_flight_code),
                coords=path
                )
flight_path.altitudemode = simplekml.AltitudeMode.absolute
flight_path.style.linestyle.width = 3
flight_path.style.linestyle.color = simplekml.Color.red
kml.save(output_file)
