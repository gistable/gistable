# Requires ModestMaps to be installed
# Don't do this unless you have a very good reason, and a MapBox account,
# and you replace the 'examples' tileset with a tileset in your account.

import ModestMaps as MM
from ModestMaps.Geo import MercatorProjection, deriveTransformation
from ModestMaps.Providers import IMapProvider
from math import pi

class MapBox(IMapProvider):
    def __init__(self):
        t = deriveTransformation(-pi, pi, 0, 0, pi, pi, 1, 0, -pi, -pi, 0, 1)
        self.projection = MercatorProjection(0, t)

    def tileWidth(self):
        return 256

    def tileHeight(self):
        return 256

    def getTileUrls(self, coordinate):
        return ('http://api.tiles.mapbox.com/v3/examples.map-vyofok3q/%d/%d/%d.png' % (coordinate.zoom, coordinate.column, coordinate.row),)

m = MM.mapByCenterZoom(MapBox(), MM.Geo.Location(37.8, -78), 13, MM.Core.Point(1200, 600))
m.draw().save('map.png')
