#!/usr/bin/env python

import requests, json, sys
import geojson

#six degrees of precision in valhalla
inv = 1.0 / 1e6;

#decode an encoded string
def decode(encoded):
    decoded = []
    previous = [0,0]
    i = 0
    #for each byte
    while i < len(encoded):
        #for each coord (lat, lon)
        ll = [0,0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            #keep decoding bytes until you have this coord
            while byte >= 0x20:
                byte = ord(encoded[i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            #get the final value adding the previous offset and remember it for the next
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        #scale by the precision and chop off long coords also flip the positions so
        #its the far more standard lon,lat instead of lat,lon
        decoded.append([float('%.6f' % (ll[1] * inv)), float('%.6f' % (ll[0] * inv))])
    #hand back the list of coordinates
    return decoded

A = [ -122.4425, 37.77823 ] # SF
B = [ -73.96625, 40.78343 ] # NY

KEY = 'API_KEY' # Get your's for free at https://mapzen.com/developers
URL = 'http://valhalla.mapzen.com/route?'
FROM_TO = '{"locations":[{"lat":'+str(A[1])+',"lon":'+str(A[0])+'},{"lat":'+str(B[1])+',"lon":'+str(B[0])+'}],"costing":"auto"}'
RST = requests.get(URL+'json='+FROM_TO+'&api_key='+KEY)
JSON = json.loads(RST.text)

line = geojson.LineString(decode(JSON['trip']['legs'][0]['shape']))
feature = geojson.Feature(geometry=line)
feature_collection = geojson.FeatureCollection([feature])

file = open('trip.json', 'w')
file.write(geojson.dumps(feature_collection, sort_keys=True))
file.close()
