# place in PokemonGo-Map directory to use with 		
# https://github.com/PokemonGoMap/PokemonGo-Map
from pogom.app import Pogom
from pogom import models
import json
from pogom.models import Pokemon, init_database
import os.path
import sys
outputFile = 'spawns.json'

app = Pogom(__name__)
db = init_database(app)

# southwest latitude and longitude, north east latitude and longitude
# @TODO - use args
swLat = None
swLng = None
neLat = None
neLng = None

query = Pokemon.select(Pokemon.latitude, Pokemon.longitude, Pokemon.disappear_time, Pokemon.spawnpoint_id)
if None not in (swLat, swLng, neLat, neLng):
    query = (query
             .where((Pokemon.latitude >= swLat) &
                    (Pokemon.longitude >= swLng) &
                    (Pokemon.latitude <= neLat) &
                    (Pokemon.longitude <= neLng)
                    )
             )
query = query.dicts()

uniq = set() # to filter duplicate spawns location at same time
spawns = []
count = 0
dupes = 0
print "Getting list of spawns"
for i in iter(list(query)):
    m = i['disappear_time'].minute
    s = i['disappear_time'].second
    spawn_sec = ((m) * 60 + (s) + 2710) % 3600
    k = (i['spawnpoint_id'], spawn_sec)
    if k not in uniq: # SQL group by, because peewee can't handle group by on aliased fields (thx Xcelled)
        uniq.add(k)
        spawns.append( { 'lat': i['latitude'], 'lng': i['longitude'], 'time': spawn_sec})
        count += 1
    else:
	    dupes += 1

print "Total unique spawns: " + str(count) + " Duplicates excluded: " +  str(dupes)

choice = 'y'
if os.path.isfile(outputFile):
    prompt = ("%s exists, overwrite?   [Y or N] " ) % outputFile
    choice = raw_input(prompt)

if choice.lower() in 'y':
    f = open(outputFile, 'w')
    f.write(json.dumps(spawns))
    f.close()
else :
    print 'Canceled writing file'
    sys.exit()
