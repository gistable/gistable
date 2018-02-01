from urllib2 import urlopen
from cStringIO import StringIO
import json
from pyproj import Proj
from shapely.geometry import Point
from geopandas import GeoSeries, GeoDataFrame

# http://www.nyc.gov/html/dcp/download/bytes/nybb_13a.zip
boros = GeoDataFrame.from_file('/nybb_13a/nybb.shp', vfs='zip://nybb_13a.zip')
url = 'http://citibikenyc.com/stations/json'
f = urlopen(url)
buffer = StringIO(f.read())
c = json.load(buffer)
df = GeoDataFrame(c['stationBeanList'])

# TODO: this should work with fiona.to_string(boros.crs)
nyp = Proj('+datum=NAD83 +lat_0=40.1666666667 +lat_1=40.6666666667 '
           '+lat_2=41.0333333333 +lon_0=-74 +no_defs +proj=lcc +units=us-ft '
           '+x_0=300000 +y_0', preserve_units=True)
s = GeoSeries([Point(x, y) for x, y in zip(*nyp(df['longitude'], df['latitude']))])
df['geometry'] = s
df.crs = boros.crs

manhattan = boros.geometry[3]
brooklyn = boros.geometry[2]
in_mn = df.geometry.within(manhattan)
in_bk = df.geometry.within(brooklyn)
print sum(in_mn), 'stations in Manhattan'
print sum(in_bk), 'stations in Brooklyn'
print sum(df['availableBikes'][in_mn]), 'available bikes in Manhattan'
print sum(df['availableBikes'][in_bk]), 'available bikes in Brooklyn'