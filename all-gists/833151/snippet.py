from itertools import tee, izip

from django.contrib.gis.db import models
from django.contrib.gis.measure import Distance

from geopy.distance import distance as geopy_distance

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

# Create your models here.
class Route(models.Model):
    name = models.CharField(max_length=100)

    def length(self):
        '''Determine the length of the route.'''
        points = (waypoint.point for waypoint in self.waypoint_set.orderby('time'))
        meters = sum(geopy_distance(a, b).meters for (a, b) in pairwise(points))
        return Distance(m=meters)

class Waypoint(models.Model):
    time = models.DateTimeField()
    route = models.ForeignKey(Route)

    point = models.PointField(srid=4326)
    objects = models.GeoManager()

def distance(*points):
    '''
    Find the geodesic distance between two or more points.

    If more than two points are specified, the points are assumed
    to be on a route. The total length of this route is
    calculated.

    Returns a django.contrib.gis.measure.Distance object.
    '''
    meters = sum(geopy_distance(a, b).meters for (a, b) in pairwise(points))
    return Distance(m=meters)

def example():
    from django.contrib.gis.geos import Point
    # Calculate the distance to San Franciso from Washington, D.C., via Chicago.
    washington = Point(38.53, 77.02)
    chicago = Point(41.50, 87.37)
    san_francisco = Point(37.47, 122.26)

    d = distance(washington, chicago, san_francisco)
    print "Washington, D.C. -> Chicago -> San Francisco:"
    print "%(miles)0.2f miles, or %(kilometers)0.2f kilometers (or %(fathoms)0.2f fathoms)" % {
            'miles': d.mi,
            'kilometers': d.km,
            'fathoms': d.fathom
    }
