#!/usr/local/bin/python

from sys import argv
import os
import math
import urllib2

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_url(zoom, xtile, ytile, download_path):
    # Switch between otile1 - otile4

    subdomain = random.randint(1, 4)
    
    url = "http://otile%d.mqcdn.com/tiles/1.0.0/osm/%d/%d/%d.png" % (subdomain, zoom, xtile, ytile)
    dir_path = "%s/tiles/%d/%d/" % (download_path, zoom, xtile)
    download_path = "%s/tiles/%d/%d/%d.png" % (download_path, zoom, xtile, ytile)
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    print "downloading %r" % url
    
    source = urllib2.urlopen(url)
    content = source.read()
    source.close()
    destination = open(download_path,'wb')
    destination.write(content)
    destination.close()

def usage():
    print "Usage: "
    print "osm_maps_downloader <south_latitude> <west_longitude> <north_latitude> <east_longitude> <min_zoom> <max_zoom> <download_path>"

def main(argv):
    try:
        script, south, west, north, east, min_zoom, max_zoom, download_path = argv
    except:
        usage()
        exit(2)

    for zoom in range(int(min_zoom), int(max_zoom) + 1, 1):
        xtile, ytile = deg2num(float(south), float(west), float(zoom))
        final_xtile, final_ytile = deg2num(float(north), float(east), float(zoom))

        for x in range(xtile, final_xtile + 1, 1):
            for y in range(ytile, final_ytile - 1, -1):
                download_url(int(zoom), x, y, download_path)            
    return 0
    
main(argv)    
