"""
Import Yahoo! GeoPlanet in to MongoDB.

This creates a geoplanet collection containing documents like this:

{
    '_id': woeid,
    'name': name,
    'iso': iso,
    'language': language,
    'placetype': placetype,
    'parent': parent,
    'ancestors': [list of all ancestors],
    'neighbours': [list of all adjacent neighbours],
    'children': [list of all direct children],
    'descendants': [list of all descendants],
}

descendants and ancestors don't work yet.

"""
import pymongo, csv

connection = pymongo.Connection()
db = connection.geoplanet

def first_pass():
    reader = csv.reader(open('geoplanet_places_7.4.1.zip'), csv.excel_tab)
    headers = reader.next()
    i = 0
    for woe_id, iso, name, language, placetype, parent_id in reader:
        done = db.places.insert({
            '_id': woe_id,
            'iso': iso,
            'name': name.decode('utf8'),
            'language': language,
            'placetype': placetype,
            'parent': parent_id,
            'ancestors': [parent_id],
            'neighbours': [],
            'children': [],
            'descendants': [],
        })
        i += 1
        if i % 1000 == 0:
            print "Done %s" % i

def second_pass():
    "Update the children"
    i = 0
    for place in db.places.find():
        parent = place.get('parent')
        if parent:
            db.places.update({'_id': parent}, {
                '$addToSet': {'children': place['_id']}
            })
        i += 1
        if i % 1000 == 0:
            print "Done %s" % i

def third_pass():
    "Import the adjacencies"
    reader = csv.reader(open('geoplanet_adjacencies_7.4.1.tsv'),csv.excel_tab)
    headers = reader.next()
    i = 0
    for woe_id, iso, woe_id_2, iso_2 in reader:
        db.places.update({'_id': woe_id}, {
            '$addToSet': {'neighbours': woe_id_2}
        })
        i += 1
        if i % 1000 == 0:
            print "Done %s" % i
