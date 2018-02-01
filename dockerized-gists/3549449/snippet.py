#!/usr/bin/env python

# Copyright 2012 Patrick Mueller
# Licensed under the Tumbolia Public License (see bottom)

# uses Google Static Maps functionality
# https://developers.google.com/maps/documentation/staticmaps/

import os
import sys
import re
import json
import time
import urllib2
import datetime
import xml.dom.minidom

from xml.dom  import Node
from urlparse import urlparse
from optparse import OptionParser

#-------------------------------------------------------------------------------
# program information
#-------------------------------------------------------------------------------
PROGRAM_NAME    = os.path.basename(sys.argv[0])
PROGRAM_VERSION = "0.1"

#-------------------------------------------------------------------------------
def main():
    (options, iKmlName) = parseCommandLine()
    
    log("reading KML file")
    kml = getKmlContents(iKmlName)
    
    doc    = xml.dom.minidom.parseString(kml)
    name   = getKmlName(doc)
    points = getKmlPoints(doc)
    icons  = getKmlIcons(doc)

    getMaps(options, name, points, icons)

#-------------------------------------------------------------------------------
def getMaps(options, mapName, points, icons):
    outDir     = options.outDir
    zoomStart  = options.zoom[0]
    zoomEnd    = options.zoom[1]
    width      = options.size
    height     = options.size
    mapRoad    = options.mapRoad
    mapTerrain = options.mapTerrain

    #---------------------------------------------------------------------------
    jIndex = {}
    jIndex["name"]       = mapName
    jIndex["width"]      = width
    jIndex["height"]     = width
    jIndex["locations"]  = []
    jIndex["overallMap"] = {}
    
    if mapRoad:
        jIndex["overallMap"]["road"]    = "map-@-R-%dx%d.png" % (width, height)

    if mapTerrain:
        jIndex["overallMap"]["terrain"] = "map-@-T-%dx%d.png" % (width, height)
        
    jLocations = jIndex["locations"]
    
    for point in points:
        location = {}
        location["name"]  = point.name
        location["label"] = point.label
        location["maps"]  = {}
        location["icon"]  = os.path.basename(icons[point.icon])
        
        jLocations.append(location)
        
        jMapsRoad    = location["maps"]["road"]    = []
        jMapsTerrain = location["maps"]["terrain"] = []
        
        for zoom in range(zoomStart, zoomEnd+1):
            if mapRoad:
                jMapsRoad.append(
                    "map-%s-%02d-R-%dx%d.png" % (point.label, zoom, width, height)
                )
        
            if mapTerrain:
                jMapsTerrain.append(
                    "map-%s-%02d-T-%dx%d.png" % (point.label, zoom, width, height)
                )
            
    jsonIndex = json.dumps(jIndex, indent=4)

    #---------------------------------------------------------------------------
    oFileName = os.path.join(outDir, "map-index.json")
    oFile = open(oFileName, "w")
    oFile.write(jsonIndex)
    oFile.close()

    log("generated %s" % oFileName)

    #---------------------------------------------------------------------------
    jsIndex = "MapIndex = %s" % jsonIndex
    
    oFileName = os.path.join(outDir, "map-index.js")
    oFile = open(oFileName, "w")
    oFile.write(jsIndex)
    oFile.close()

    log("generated %s" % oFileName)
    
    #---------------------------------------------------------------------------
    if mapRoad:
        getImage(
            outDir, 
            "map-@-R-%dx%d.png" % (width,height), 
            mapURL(points, width=width, height=height, type="roadmap")
        )
    
    if mapTerrain:
        getImage(
            outDir, 
            "map-@-T-%dx%d.png" % (width,height), 
            mapURL(points, width=width, height=height, type="terrain")
        )

    for id in icons:
        icon = icons[id]
        
        basename = os.path.basename(icon)
        getImage(outDir, basename, icon)
    
    for point in points:
        name  = point.name
        label = point.label
        lon   = point.lon
        lat   = point.lat
        
        center = "%s,%s" % (lat, lon)
        
        fName = "map-%s" % label
        
        for zoom in range(zoomStart, zoomEnd+1):
        
            if mapRoad:
                url = mapURL(
                    points, 
                    width  = width, 
                    height = height, 
                    type   = "roadmap", 
                    zoom   = zoom, 
                    center = center
                )
                getImage(
                    outDir, 
                    "%s-%02d-R-%dx%d.png" % (fName, zoom, width, height), 
                    url
                )
                
            if mapTerrain:
                url = mapURL(
                    points, 
                    width  = width, 
                    height = height, 
                    type   = "terrain", 
                    zoom   = zoom, 
                    center = center
                )
                getImage(
                    outDir, 
                    "%s-%02d-T-%dx%d.png" % (fName, zoom, width, height), 
                    url
                )

#-------------------------------------------------------------------------------
def mapURL(points, width=320, height=320, center=None, zoom=None, type="roadmap"):
    
    parms = []
    parms.append("size=%dx%d" % (width, height))
    parms.append("sensor=false")
    
    if center: parms.append("center=%s"  % center)
    if zoom:   parms.append("zoom=%s"    % str(zoom))
    if type:   parms.append("maptype=%s" % type)
    
    markers = []
    for point in points:
        parms.append("markers=color:red%%7Clabel:%s%%7C%s,%s" % (point.label, point.lat, point.lon))
    
    parms = "&".join(parms)
    
    return "http://maps.googleapis.com/maps/api/staticmap?%s" % parms

#-------------------------------------------------------------------------------
def getImage(outDir, name, url):
    oFileName = os.path.join(outDir,name)

    if os.path.exists(oFileName): 
        log("skipping generated file %s" % name)
        return
    
    log("downloading %s" % oFileName)
    
    time.sleep(1)
    
    iFile = urllib2.urlopen(url)
    content = iFile.read()
    iFile.close()
    
    oFile = open(oFileName, "w")
    oFile.write(content)
    oFile.close()

#-------------------------------------------------------------------------------
def getKmlContents(name):
    bits = urlparse(name)
    
    scheme = bits.scheme
    if scheme == "": scheme = "file"
    
    if scheme == "file":
        iFile = open(bits.path, "r")
    else:
        iFile = urllib2.urlopen(url)
        
    contents = iFile.read()
    iFile.close()
    
    return contents

#-------------------------------------------------------------------------------
def getKmlName(doc):
    elems = doc.getElementsByTagName("Document")
    if len(elems) == 0: fatal("unable to get Document element from kml")
    
    elems = elems[0].getElementsByTagName("name")
    if len(elems) == 0: fatal("unable to get Document/name element from kml")
    
    return getText(elems[0])

#-------------------------------------------------------------------------------
def getKmlPoints(doc):
    result = []

    elems = doc.getElementsByTagName("Document")
    if len(elems) == 0: fatal("unable to get Document element from kml")
    
    label = "A"
    doc   = elems[0]
    for child in doc.childNodes:
        if child.nodeType != Node.ELEMENT_NODE: continue
        if child.tagName  != "Placemark": continue
        
        elems = child.getElementsByTagName("name")
        if len(elems) == 0: 
            continue
            
        name = getText(elems[0])

        elems = child.getElementsByTagName("styleUrl")
        if len(elems) == 0: 
            continue
            
        icon = getText(elems[0])
        
        elems = child.getElementsByTagName("Point")
        if len(elems) == 0: 
            continue
        
        elems = elems[0].getElementsByTagName("coordinates")
        if len(elems) == 0: 
            continue
            
        coords = getText(elems[0])
        
        coords = coords.split(",")[0:2]
        lon    = coords[0]
        lat    = coords[1]
        
        result.append(Location(name, label, lon, lat, icon))
        
        label = chr(ord(label)+1)
        
        if len(result) >= 26:
            log("> 26 locations specified, only 26 will be plotted")
            return result
    
    return result

#-------------------------------------------------------------------------------
def getKmlIcons(doc):
    result = {}

    elems = doc.getElementsByTagName("Document")
    if len(elems) == 0: fatal("unable to get Document element from kml")
    
    doc   = elems[0]
    for child in doc.childNodes:
        if child.nodeType != Node.ELEMENT_NODE: continue
        if child.tagName  != "Style": continue
        
        if not child.hasAttribute("id"):
            continue

        id = "#%s" % child.getAttribute("id")
        
        elems = child.getElementsByTagName("IconStyle")
        if len(elems) == 0: 
            continue
            
        elems = elems[0].getElementsByTagName("Icon")
        if len(elems) == 0: 
            continue
            
        elems = elems[0].getElementsByTagName("href")
        if len(elems) == 0: 
            continue
            
        url = getText(elems[0])
        
        result[id] = url

    return result

#-------------------------------------------------------------------------------
def getText(node):
    result = ""
    
    for child in node.childNodes:
        if   child.nodeType == Node.TEXT_NODE:    result += child.nodeValue
        elif child.nodeType == Node.ELEMENT_NODE: result += getText(child)
        
    return result

#-------------------------------------------------------------------------------
class Location:
    def __init__(self, name, label, lon, lat, icon):
        self.name  = name
        self.label = label
        self.lon   = lon
        self.lat   = lat
        self.icon  = icon

#-------------------------------------------------------------------------------
# parse commandline
#-------------------------------------------------------------------------------
def parseCommandLine():

    usage = """usage: %prog [options] kml-file

    Download static Google maps and make a json index."""

    # build parser
    parser = OptionParser(
        usage   = usage,
        version = "%prog " + PROGRAM_VERSION
    )

    # add options
    parser.add_option("-o", "--out",
        dest    = "outDir",
        metavar = "DIR",
        default = ".",
        help    = "output directory (default: %default)"
    )
    
    parser.add_option("-z", "--zoom",
        dest    = "zoom",
        default = "15-17",
        help    = "range of zoom values (default: %default)"
    )
    
    parser.add_option("-s", "--size",
        dest    = "size",
        type    = "int",
        default = 320,
        help    = "width/height of image (default: %default)"
    )
    
    parser.add_option("-r", "--road",
        dest    = "mapRoad",
        action  = "store_true",
        default = True,
        help    = "generate road map  (default: %default)"
    )
    
    parser.add_option("-t", "--terrain",
        dest    = "mapTerrain",
        action  = "store_true",
        default = False,
        help    = "generate terrain map  (default: %default)"
    )
    
    # parse!
    (options, iKmlName) = parser.parse_args()

    patternZoom = re.compile("\d+-\d+")
    
    if not patternZoom.match(options.zoom):
        fatal("zoom should be specified as ###-###")
        
    zooms = options.zoom.split("-")[0:2]
    zooms[0] = int(zooms[0])
    zooms[1] = int(zooms[1])
    
    if zooms[0] > zooms[1]:
        tmp      = zooms[0]
        zooms[0] = zooms[1]
        zooms[1] = tmp
        
    if  zooms[0] < 0:
        zooms[0] = 0
        
    if  zooms[1] > 21:
        zooms[1] = 21
    
    options.zoom = zooms
        
    # print "options: %s" % repr(options)
    
    # check input kml name
    if 0 == len(iKmlName):
        parser.print_help()
        sys.exit()
        
    iKmlName = iKmlName[0]
    
    if not os.path.exists(iKmlName):
        fatal("input file does not exist: %s" % iKmlName)
        
    # check output directory name
    options.outDir = options.outDir.rstrip("/")
    if not os.path.exists(options.outDir):
        fatal("output directory does not exist: %s" % options.outDir)
        
    if not os.path.isdir(options.outDir):
        fatal("output directory is not a directory: %s" % options.outDir)

    # return the goodies
    return (options, iKmlName)

#-------------------------------------------------------------------------------
# log a message
#-------------------------------------------------------------------------------
def log(message):
    print "%s: %s" % (PROGRAM_NAME, message)
    
#-------------------------------------------------------------------------------
# log a fatal message
#-------------------------------------------------------------------------------
def fatal(message):
    log(message)
    sys.exit(1)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
# Tumbolia Public License
#-------------------------------------------------------------------------------
# Copying and distribution of this file, with or without modification, are
# permitted in any medium without royalty provided the copyright notice and
# this notice are preserved.
# 
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#    0. opan saurce LOL
#-------------------------------------------------------------------------------
