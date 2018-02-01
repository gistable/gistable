#!/usr/bin/env python

from __future__ import print_function

import psycopg2
import bs4
import requests
import sys

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

#printing to stderr
def warning(*objs):
    print(*objs, file=sys.stderr)


def s57_description(layer_name):
    ''' Generate descriptions for s57 layers by querying s-57.com '''
    description_url = "http://www.s-57.com/Object.asp?nameAcr=" + layer_name.upper()
    page = requests.get(description_url)
    soup = bs4.BeautifulSoup(page.text)
    dts = soup.select("dd")

    if len(dts) > 0:
        try:
            description = str(dts[0].text).strip()
            return description
        except:
            warning("error parsing description for " + layer_name)
            
    return default_description(layer_name)


def default_description(layer_name):
    ''' Generate a generic description '''
    return "Auto generated from table " + layer_name


description_function = default_description
buffer_size = 0
srs_90013 = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
srs_wgs84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
srs = srs_90013

#limit the number of layers that will be processed, usefull for testing, set to -1 for no limit
layer_limit = -1

#connect to postgres
dbname = 'enc'
dbuser = 'jesse'
dbhost = 'localhost'
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s'" % (dbname, dbuser, dbhost))
except Exception, e:
    warning("Failed to connect to database", e)
    exit(-1)

source = {}
source['_prefs'] = {
    'disabled' : [], 
    'inspector' : False,
    'mapid' : '',
    'rev' : '',
    'saveCenter' : False
}

source['attribution'] = 'Auto generated from db ' + dbname
source['center'] = [0, 0, 2]
source['descripion'] = ''
source['name'] = dbname
source['maxzoom'] = 14
source['minzoom'] = 0

layers = []
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' order by table_name")

allrows = cur.fetchall()

#mapping between postgres types and tm2 types
field_types = (
    ('Number', ['numeric', 'integer', 'double precision']),
    ('String', ['character varying'])
)


for row in allrows:
    table_name = row[0]

    #get extent for all features in layer, if this fails, then the table doesnt have a geometry column
    try:
        cur.execute("SELECT ST_XMin(r) AS xmin, ST_YMin(r) AS ymin, ST_XMax(r) AS xmax, ST_YMax(r) AS ymax FROM (SELECT ST_Collect(wkb_geometry) AS r FROM %s) AS foo" % table_name)
        bounds = cur.fetchone()
    except:
        conn.rollback()
        warning("skipping table " + table_name) 
        continue

    #get list of fields
    fields = {}
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name ='%s'" % table_name)
    for (column_name, column_type) in cur.fetchall():
        for (name, values) in field_types:
            if column_type in values:
                fields[column_name] = name
                break

    datasource = {
        'dbname': dbname,
        'geometry_field': '',
        'geometry_table': '',
        'host': dbhost,
        'key_field': '',
        'max_size': 512,
        'port': '',
        'table' : table_name,
        'type': 'postgis',
        'user' : dbuser,
        'extent': ",".join([str(x) for x in bounds])
    }

    layer = {
        'id' : table_name,
        'fields': fields,
        'Datasource': datasource,
        'description': '',
        'srs' : srs,
        'properties' : {'buffer-size' : buffer_size}
    }
    if description_function:
        layer['description'] = description_function(table_name)

    layers.append(layer)

    if layer_limit > 0:
        if len(layers) >= layer_limit:
            break


source['Layer'] = layers

print(dump(source, default_flow_style=False))
