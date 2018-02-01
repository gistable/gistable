import pyproj
from shapely.geometry import shape
from shapely.ops import transform

geom = {'type': 'Polygon',
        'coordinates': [[[-122., 37.], [-125., 37.],
	                     [-125., 38.], [-122., 38.],
                         [-122., 37.]]]}

s = shape(geom)
proj = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'),
               pyproj.Proj(init='epsg:3857'))

s_new = transform(proj, s)

projected_area = transform(proj, s).area
