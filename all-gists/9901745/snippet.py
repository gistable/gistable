from osgeo import ogr
from osgeo import osr

source = osr.SpatialReference()
source.ImportFromEPSG(4326)

target = osr.SpatialReference()
target.ImportFromEPSG(3857)

transform = osr.CoordinateTransformation(source, target)

geojson = """{ "type": "LineString", "coordinates": [ [ -75.313585, 43.069271 ], [ -75.269426, 43.114027 ], [ -75.158731, 43.114325 ] ] }"""
geom = ogr.CreateGeometryFromJson(geojson)
geom.Transform(transform)
print "Length = %d" % geom.Length() + " meters"