#! /usr/bin/env python

import json
import time
import shelve
import urllib
import urllib.request

DB = 'flights'
API = "http://www.flightradar24.com/zones/full_all.json"
FREQ = 60 * 5
# FREQ = 5
DURATION = 3600 * (24 + 9)
# DURATION = 20
MIN_ALT = 28500
MIN_LAT = 40
MAX_LAT = 57
MIN_LON = -40
MAX_LON = -25

start = time.time()

db = shelve.open(DB, protocol=3)
db['start'] = start
db.close()

# For log output
log = "{} {} {} {},{},{}"
logfile = open("log.txt", 'w+')

while time.time() - start < DURATION:

  db = shelve.open(DB, protocol=3)

  # timestamp (date of retrieval on our side)
  ts = int(time.time())

  try:
    data = json.loads(urllib.request.urlopen(url=API).read().decode("utf-8"))
  except urllib.error.URLError:
    continue

  for k, v in data.items():
  
    try:
      lat, lon, heading, alt, plane, flight = int(v[1]), int(v[2]), int(v[3]), int(v[4]), v[8], v[16]
    except TypeError:
      # v is not a list or has an incorrect format
      continue
    except IndexError:
      # v has an incorrect format
      continue
  
    # Filter flights we are not interested in
    if not flight or flight.isspace():
      continue
    if not plane or plane.isspace():
      continue
    if plane == flight: # private flights
      continue
    if alt < MIN_ALT:
      continue
    if lat < MIN_LAT or lat > MAX_LAT:
      continue
    if lon < MIN_LON or lon > MAX_LON:
      continue
    
    # Get entry or create it if necessary
    try:
      entry = db[flight]
      status = "*"
    except KeyError:
      entry = (plane, [])
      status = "+"
    print(log.format(status, flight, plane, ts, heading, alt), file=logfile)

    # Update entry
    entry[1].append((ts, heading, alt))

    # Write back entry to the db
    db[flight] = entry

  db.close()
  logfile.flush()
  time.sleep(FREQ)

print("Stop after", int(time.time() - start), "s")
logfile.close()
