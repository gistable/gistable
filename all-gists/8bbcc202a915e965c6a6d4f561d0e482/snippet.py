'''
Requirements:
    geographiclib==1.46.3
    pyproj==1.9.5.1
    geopy==1.11.0
    git+https://github.com/xoolive/geodesy@c4eb611cc225908872715f7558ca6a686271327a
'''
from math import radians, sin, cos, asin, sqrt, pi, atan, atan2, fabs
from time import time
import geopy.distance
import pyproj
from geographiclib.geodesic import Geodesic, Constants

import geodesy.sphere as geo

geod = pyproj.Geod(ellps='WGS84')
geodesic = Geodesic(a=Constants.WGS84_a,f=Constants.WGS84_f)

p_minsk = (27.561831, 53.902257)
p_moscow = (37.620393, 55.75396)

# https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
EARTH_MEAN_RADIUS = 6371008.8
EARTH_MEAN_DIAMETER = 2 * EARTH_MEAN_RADIUS

# https://en.wikipedia.org/wiki/Earth_radius#Equatorial_radius
EARTH_EQUATORIAL_RADIUS = 6378137.0
EARTH_EQUATORIAL_METERS_PER_DEGREE = pi * EARTH_EQUATORIAL_RADIUS / 180 # 111319.49079327358
I_EARTH_EQUATORIAL_METERS_PER_DEGREE = 1 / EARTH_EQUATORIAL_METERS_PER_DEGREE

def approximate_distance(point1, point2):
    '''
        Approximate calculation distance
        (expanding the trigonometric functions around the midpoint)
    '''

    lon1, lat1 = (radians(coord) for coord in point1)
    lon2, lat2 = (radians(coord) for coord in point2)
    cos_lat = cos((lat1+lat2)/2.0)
    dx = (lat2 - lat1)
    dy = (cos_lat*(lon2 - lon1))
    return EARTH_MEAN_RADIUS*sqrt(dx**2 + dy**2)


def haversine_distance(point1, point2):
    '''
        Calculating haversine distance between two points
        (see https://en.wikipedia.org/wiki/Haversine_formula,
            https://www.math.ksu.edu/~dbski/writings/haversine.pdf)

        Is numerically better-conditioned for small distances
    '''
    lon1, lat1 = (radians(coord) for coord in point1[:2])
    lon2, lat2 = (radians(coord) for coord in point2[:2])
    dlat = (lat2 - lat1)
    dlon = (lon2 - lon1)
    a = (
        sin(dlat * 0.5)**2 +
        cos(lat1) * cos(lat2) * sin(dlon * 0.5)**2
    )

    return EARTH_MEAN_DIAMETER * asin(sqrt(a))


def great_circle(point1, point2):
    '''
        Calculating great-circle distance
        (see https://en.wikipedia.org/wiki/Great-circle_distance)
    '''
    lon1, lat1 = (radians(coord) for coord in point1)
    lon2, lat2 = (radians(coord) for coord in point2)

    dlon = fabs(lon1 - lon2)
    dlat = fabs(lat1 - lat2)

    numerator = sqrt(
        (cos(lat2)*sin(dlon))**2 +
        ((cos(lat1)*sin(lat2)) - (sin(lat1)*cos(lat2)*cos(dlon)))**2)

    denominator = (
        (sin(lat1)*sin(lat2)) +
        (cos(lat1)*cos(lat2)*cos(dlon)))

    c = atan2(numerator, denominator)
    return EARTH_MEAN_RADIUS*c

# 1
t = time()
for i in range(1000000):
    distance = haversine_distance(p_minsk, p_moscow)
print("#1 haversine fun: %s (%s)" % (distance, time() - t))

# 2
t = time()
for i in range(1000000):
    distance = great_circle(p_minsk, p_moscow)
print("#2 great circle fun: %s (%s)" % (distance, time() - t))

# 3
t = time()
for i in range(1000000):
    distance = geopy.distance.vincenty(p_minsk[::-1], p_moscow[::-1], ellipsoid='WGS-84').meters
print("#3 geopy: %s (%s)" %  (distance, time() - t))

# 4
# http://jswhit.github.io/pyproj/pyproj.Geod-class.html#inv
t = time()
for i in range(1000000):
    _az12, _az21, distance = geod.inv(*list(p_minsk + p_moscow))
print("#4 pyproj: %s (%s)" % (distance, time() - t))

# 5
# http://geographiclib.sourceforge.net/1.46/python/code.html#geographiclib.geodesic.Geodesic.Inverse
t = time()
for i in range(1000000):
    r = geodesic.Inverse(*(p_minsk[::-1] + p_moscow[::-1]), outmask=geodesic.DISTANCE)
print("#5 geographiclib: %s (%s)" % (r['s12'], time() - t))

# 6
# https://github.com/xoolive/geodesy
t = time()
for i in range(1000000):
    d = geo.distance(p_minsk[::-1], p_moscow[::-1])
print("#6 geodesy: %s (%s)" % (d, time() - t))

'''
#1 haversine fun: 675656.2994818708 (2.1997811794281006)
#2 great circle fun: 675656.2994818711 (2.8947739601135254)
#3 geopy: 677789.5312317797 (32.68954396247864)
#4 pyproj: 677789.531232748 (11.323993921279907)
#5 geographiclib: 677789.5312327482 (195.3897831439972)
#6 geodesy: 675655.366226931 (0.7595169544219971)
'''


'''
Using PostGIS

# select ST_Length(ST_GeomFromText('LINESTRING(27.561831 53.902257, 37.620393 55.75396)',4326), true) as length;
      length
------------------
 677789.531232748
(1 row)
'''
