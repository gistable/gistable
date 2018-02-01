import csv
import json


def dms2latlng(value):
    """
    Degres Minutes Seconds to Decimal degres
    """
    degres, minutes, seconds = value.split()
    seconds, direction = seconds[:-1], seconds[-1]
    dec = float(degres) + float(minutes)/60 + float(seconds)/3600
    if direction in ('S', 'W'):
        return -dec
    return dec


csv_file = 'Pub9volA130819x.flatfile.txt'
geojson_file = csv_file.replace('.txt', '.geojson')
reader = csv.DictReader(open(csv_file, 'rb'), delimiter="\t")

geojson = dict(type='FeatureCollection', features=[])

for line in reader:

    lng = dms2latlng(line.pop('Longitude'))
    lat = dms2latlng(line.pop('Latitude'))
    wmoid = int(line.pop('StationId'))

    props = dict(name=line.pop('StationName').title(),
                 wmoid=wmoid,
                 model='webmap.WeatherStation')

    geom = dict(type='Point',
                coordinates=[lng, lat])
    feature = dict(type='Feature',
                   id=wmoid,
                   geometry=geom,
                   properties=props)
    geojson['features'].append(feature)

json.dump(geojson, open(geojson_file, 'wb'))