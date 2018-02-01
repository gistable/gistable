#!/usr/bin/env python
 
"""A tiny script that polls your location on Google Latitude, and updates
the color of a Blink1 LED. http://shop.thingm.com/blink1/
 
Red = At work
Blue = At home
Green = On my way
 
Should work on Windows, OS-X and Linux. Requires Python 2.7 or later.
 
Instructions:
1: Download the blink-1-tool and put in the current directory: http://thingm.com/products/blink-1.html
2: Update your user ID (see http://bestfromgoogle.blogspot.com/2011/05/easier-way-to-use-google-latitude-api.html)
3: Update your home and work latitudes.

See: http://joewalnes.com/2012/12/14/blink1-google-latitude-wheres-daddy/
 
"""

#### Config

user_id = 'FILL THIS IN' 
# Latitude, Longitude
work = (41.882217, -87.641367)
home = (THIS, BIT)
 
#### End of config
 
import atexit
import json
import urllib
import subprocess
from time import sleep
from math import sqrt
 
poll_interval = 20 # in seconds
 
def get_coords(user_id):
    """Return (latitude, longitude)"""
    url = 'http://www.google.com/latitude/apps/badge/api?user=%s&type=json' % user_id
    content = urllib.urlopen(url)
    try:
        data = json.load(content)
        coords = data['features'][0]['geometry']['coordinates']
        return coords[1], coords[0]
    finally:
	content.close()
 
def distance(coord1, coord2):
    """Dumb implementation. Doesn't take into account curvature of earth, but good enough for my commute home."""
    return sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
 
def blink_tool(arg):
    subprocess.Popen(['./blink1-tool', arg]).wait()
 
def main():
    atexit.register(lambda: blink_tool('--off'))
    while True:
        try:
            current_coords = get_coords(user_id)
            current_distance = distance(current_coords, home)
            max_distance = distance(work, home)
            ratio = min(1.0, max(current_distance / max_distance, 0)) # value from 0.0 (home) to 1.0 (work)
            print 'Position:%s Ratio:%s' % (current_coords, ratio)
            if ratio < 0.05:
                blink_tool('--blue') # home
            elif ratio > 0.95:
                blink_tool('--red') # work
            else:
                blink_tool('--green') # commuting
        except Exception as e:
            print 'Error', e 
        sleep(poll_interval)
 
if __name__ == '__main__':
    main()