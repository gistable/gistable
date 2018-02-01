#!/usr/bin/env python

# This script is like generate_image.py from the OSM Mapnik code,
# but it renders based on a given centre point, zoom and final image pixel size

# Author: Andrew Harvey <andrew.harvey4@gmail.com>
# License: CC0 http://creativecommons.org/publicdomain/zero/1.0/
#
# To the extent possible under law, the person who associated CC0
# with this work has waived all copyright and related or neighboring
# rights to this work.
# http://creativecommons.org/publicdomain/zero/1.0/

# For testing the tile 17/120590/78656 should match the output of
# ./render_map_preview.py -x 151.21170043945312 -y -33.871555787081476 -z 17 -w 256 -h 256

# that tile has centre (-33.871555787081476, 151.21170043945312) -> 16832809.4949049 -4011568.11846262
# and bounds (-33.87041555094183, 151.2103271484375),(-33.87269600798948, 151.21307373046875)
# which are projected as (gdaltransform -s_srs '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs' -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
#    xmin=16832656.6208484
#    ymin=-4011415.24440605 
#    xmax=16832962.3689615
#    ymax=-4011720.99251919

#    dx=306 ie. so 306 in projected units for this one tile

try:
    import mapnik2 as mapnik
except:
    import mapnik

import getopt, sys, os

# target projection
merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')

# WGS lat/long source projection of centre
longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

# ensure minimum Mapnik version
if not hasattr(mapnik,'mapnik_version') and not mapnik.mapnik_version() >= 600:
    raise SystemExit('This script requires Mapnik >=0.6.0)')

if __name__ == "__main__":
    # get arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:x:y:z:w:h:o:", ["mapfile=", "centrex=", "centrey=", "zoom=", "width=", "height=", "output="])
    except getopt.GetoptError, err:
        print str(err)
        #usage()
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-m", "--mapfile"):
            mapfile = a
        elif o in ("-x", "--centrex"):
            centrex = float(a)
        elif o in ("-y", "--centrey"):
            centrey = float(a)
        elif o in ("-z", "--zoom"):
            zoom = int(a)
        elif o in ("-w", "--width"):
            width = int(a)
        elif o in ("-h", "--height"):
            height = int(a)
        elif o in ("-o", "--output"):
            output = a

    # make a new Map object for the given mapfile
    m = mapnik.Map(width, height)
    mapnik.load_map(m, mapfile)
    
    # ensure the target map projection is mercator
    m.srs = merc.params()
    
    # transform the centre point into the target coord sys
    centre = mapnik.Coord(centrex, centrey)  
    transform = mapnik.ProjTransform(longlat, merc)
    merc_centre = transform.forward(centre)
    
    # 360/(2**zoom) degrees = 256 px
    # so in merc 1px = (20037508.34*2) / (256 * 2**zoom)
    # hence to find the bounds of our rectangle in projected coordinates + and - half the image width worth of projected coord units
    dx = ((20037508.34*2*(width/2)))/(256*(2 ** (zoom)))
    minx = merc_centre.x - dx
    maxx = merc_centre.x + dx
    
    # grow the height bbox, as we only accurately set the width bbox
    m.aspect_fix_mode = mapnik.aspect_fix_mode.ADJUST_BBOX_HEIGHT

    bounds = mapnik.Box2d(minx, merc_centre.y-10, maxx, merc_centre.y+10) # the y bounds will be fixed by mapnik due to ADJUST_BBOX_HEIGHT
    m.zoom_to_box(bounds)

    # render the map image to a file
    mapnik.render_to_file(m, output)
     
    sys.stdout.write('output image to %s!\n' % output)
