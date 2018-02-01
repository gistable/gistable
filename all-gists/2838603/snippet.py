#!/usr/bin/env python
# distance_from_shore.py: compute true distance between points 
# and closest geometry.

# shaun walbridge, 2012.05.15

# TODO: no indexing used currently, could stand if performance needs 
# improving (currently runs in ~1.5hr for 13k points)

from geopy import distance
from osgeo import ogr
from shapely.geometry import Point, MultiPolygon
from shapely.wkt import dumps, loads

import math
import sys

# pairs iterator:
# http://stackoverflow.com/questions/1257413/1257446#1257446
def pairs(lst):
    i = iter(lst)
    first = prev = i.next()
    for item in i:
        yield prev, item
        prev = item
    yield item, first

# these methods rewritten from the C version of Paul Bourke's
# geometry computations:
# http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/
def magnitude(p1, p2):
    vect_x = p2.x - p1.x
    vect_y = p2.y - p1.y
    return math.sqrt(vect_x**2 + vect_y**2)

def intersect_point_to_line(point, line_start, line_end):
    line_magnitude =  magnitude(line_end, line_start)
    u = ((point.x - line_start.x) * (line_end.x - line_start.x) + \
         (point.y - line_start.y) * (line_end.y - line_start.y)) \
         / (line_magnitude ** 2)
    intersect_point = None
    # closest point does not fall within the line segment, 
    # take the shorter distance to an endpoint
    if u < 0.00001 or u > 1:
        ix = magnitude(point, line_start)
        iy = magnitude(point, line_end)
        if ix > iy:
            intersect_point = line_end
        else:
            intersect_point = line_start
    else:
        ix = line_start.x + u * (line_end.x - line_start.x)
        iy = line_start.y + u * (line_end.y - line_start.y)
        intersect_point = Point([ix, iy])
    return intersect_point

# convert OGR readable format to WKT representation
def ogrWkt2Shapely(input_shape):
    # this throws away the other attributes of the feature, but is 
    # sufficient in this use case
    shapely_objects=[]
    shp = ogr.Open(input_shape)
    lyr = shp.GetLayer()
    for n in range(0, lyr.GetFeatureCount()):
        feat = lyr.GetFeature(n)
        wkt_feat = loads(feat.geometry().ExportToWkt())
        shapely_objects.append(wkt_feat)
    return shapely_objects

def toLon(x):
    if x > 180:
        lon = x - 360
    else:
        lon = x
    return lon

# use the vincenty formula to get accurate distance measurements
def sphereDistance(from_point, to_point):
    distance.VincentyDistance.ELLIPSOID = 'WGS-84'
    return distance.distance((toLon(from_point.x), from_point.y), \
                             (toLon(to_point.x), to_point.y))

def findIntersectionPoint(from_point, to_polygon):
    nearest_point = None
    min_dist = float(sys.maxint)
    for seg_start, seg_end in pairs(list(to_polygon.exterior.coords)[:-1]):
        line_start = Point(seg_start)
        line_end = Point(seg_end)
        intersection_point = intersect_point_to_line(from_point, line_start, line_end)
        cur_dist =  magnitude(from_point, intersection_point)
        if cur_dist < min_dist:
            min_dist = cur_dist
            nearest_point = intersection_point
    return nearest_point

def computeLinearDistance(from_point, to_polygon):
    # first, find the intersection point with the geometry
    to_point = findIntersectionPoint(from_point, to_polygon)
    # compute the distance on the sphere
    dist = sphereDistance(from_point, to_point)
    print "from %s to %s: %f" % (from_point.wkt, to_point.wkt, dist.meters)
    return dist.meters


def computeDistance(from_geom, to_geom):
    min_dist = float(sys.maxint)
    for g in to_geom:
        # returns results in DD, approximate true dist
        dist = g.distance(from_geom) * 111 * 1000
        if dist < min_dist:
            #print "computed dist: %f" % dist
            min_dist = dist
            to_poly = g
    return computeLinearDistance(from_geom, to_poly)

data_dir = '/data/project/marinesdm/Original_Datasets/' + \
    'Supporting_Datasets/Land_Mask_SRTM_SWBD_GSHHS'

# around 200m of memory RES with these two objects loaded
print "loading data...",
sys.stdout.flush()
land = ogrWkt2Shapely("%s/%s" % \
    (data_dir, 'merge_swbd_gshhs_land_corals.shp'))
sites = ogrWkt2Shapely("%s/%s" % \
    (data_dir, 'sites_rasterized.shp'))
print " done."
sys.stdout.flush()

distances = []
f = open("%s/%s" % (data_dir, 'dists.csv'), 'w')
i = 1
for site in sites:
    if i % 10 == 0:
        print "%i..." % i
    dist = computeDistance(site, land)
    f.write("%f,%f,%f\n" % (toLon(site.x), site.y, dist))
    i+=1
f.close()
