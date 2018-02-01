#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Translate DC building shapefiles with ogr2osm https://github.com/pnorman/ogr2osm
#
# Run:
# python ogr2osm/ogr2osm.py buildings.shp -t ogr2osm/translations/dcbuildings.py
#
# This will create a buildings.osm file ready to be opened, *reviewed* and uploaded with JOSM or Potlatch.
#
# This is preliminary code, not ready to be used for an import yet.
#
# Modified from ixbarth include square/lot, pubdate, dataset, etc. as laid out in 
# http://wiki.openstreetmap.org/wiki/Washington_DC/DCGIS_imports

from pprint import pprint
    
def filterTags(attrs):
    if not attrs:
        return
    tags = {}
    tags['building'] = 'yes'
    tags['source'] = 'dcgis'
    tags['dataset'] = 'BldgPly'
    tags['dcgis:pubdate']='2011-04-29'
    if 'ADDRNUM' in attrs and attrs['ADDRNUM']:
        tags['addr:housenumber'] = attrs['ADDRNUM']
    if 'ADDRNUMSUF' in attrs and attrs['ADDRNUMSUF']:
      tags['addr:housenumber'] = tags['addr:housenumber'] + " " + attrs['ADDRNUMSUF']
    if 'STNAME' in attrs and 'STREET_TYP' in attrs  and 'QUADRANT' in attrs and attrs['STNAME']:
        tags['addr:street'] = '%s %s %s' % (attrs['STNAME'].lower(), attrs['STREET_TYP'].lower(), attrs['QUADRANT'])
    if 'GIS_ID' in attrs:
        tags['dcgis:gid'] = attrs['GIS_ID']
    if	'SQUARE' in attrs and attrs['SQUARE']:
    	tags['dcgis:square'] = attrs['SQUARE']
    if  'LOT' in attrs and attrs['LOT']:
    	tags['dcgis:lot'] = attrs['LOT']
    if 'ADDRESS_ID' in attrs and attrs['ADDRESS_ID']:
        tags['dcgis:aid'] = str(int(float(attrs['ADDRESS_ID']))) if '.' in attrs['ADDRESS_ID'] else str(int(attrs['ADDRESS_ID']))
    if 'CAPTUREYEA' in attrs and len(attrs['CAPTUREYEA']) is 10:
    	tags['dcgis:captureyear'] = attrs['CAPTUREYEA'][:4] + "-" + attrs['CAPTUREYEA'][5:7] + "-" + attrs['CAPTUREYEA'][8:10]

    
        
    return tags
