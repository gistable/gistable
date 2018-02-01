#!/usr/bin/env python
from PIL import Image

import math
import requests
import StringIO

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def getRangeForImages(lat_min, lon_min, lat_max, lon_max, zoom):
    mi = deg2num(lat_min, lon_min, zoom)
    ma = deg2num(lat_max, lon_max, zoom)
    return (mi, ma)

def sizeOfImage(lat_min, lon_min, lat_max, lon_max, zoom):
    mi, ma = getRangeForImages(lat_min, lon_min, lat_max, lon_max, zoom)
    width = abs(mi[0] - ma[0])
    height = abs(mi[1] - ma[1])
    return (width * 256, height * 256)

def loadImages(lat_min, lon_min, lat_max, lon_max, zoom):
    mi, ma = getRangeForImages(lat_min, lon_min, lat_max, lon_max, zoom)
    startx = min(mi[0], ma[0])
    starty = min(mi[1], ma[1])
    endx = max(mi[0], ma[0])
    endy = max(mi[1], ma[1])
    images = {}
    coords = []
    for i in range(startx, endx+1):
        for j in range(starty, endy+1):
            URL = "http://otile1.mqcdn.com/tiles/1.0.0/sat/%d/%d/%d.png" % (zoom, i, j)
            r = requests.get(URL)
            if r.status_code != 200:
                import sys
                print "Error loading URL: " + URL
                sys.exit(1)
            im = Image.open(StringIO.StringIO(r.content))
            coords.append((i,j))
            images[(i,j)] = im
    return (coords, images)

def createMap(lat_min, lon_min, lat_max, lon_max, zoom):
    width, height = sizeOfImage(lat_min, lon_min, lat_max, lon_max, zoom)
    coords, images = loadImages(lat_min, lon_min, lat_max, lon_max, zoom)
    lowerLeft = deg2num(lat_min, lon_min, zoom)
    x = lowerLeft[0]
    y = lowerLeft[1]

    w = width/256
    h = height/256
    im = Image.new("RGB", (width, height))
    for i in coords:
        toPaste = images[i]
        im.paste(toPaste, box=((i[0] - x) * 256, (i[1]+h - y) * 256))
    im.save("landscape.png")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4 and len(sys.argv) != 6:
        print "usage: %s zoom lat_max lon_min [lat_min lon_max]" % sys.argv[0]
        sys.exit(-1)
    zoom = int(sys.argv[1])
    lat_max = float(sys.argv[2])
    lon_min = float(sys.argv[3])
    lat_min = math.floor(lat_max - 0.5)
    lon_max = math.ceil(lon_min + 0.5)
    if len(sys.argv) == 6:
        lat_min = float(sys.argv[4])
        lon_max = float(sys.argv[5])
    createMap(lat_min, lon_min, lat_max, lon_max, zoom)
