#
# you might want to run this first:
#
# pip install pyproj mercantile
#
from pyproj import Proj
import mercantile

mercator = Proj('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +over +no_defs')
albers = Proj('+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +ellps=sphere +towgs84=0,0,0,0,0,0,0 +units=m +no_defs +nadgrids=@null')

min_z = 5
max_z = 12

def get_tile(lon, lat, z):
    pt = albers(lon, lat)
    pt2 = mercator(pt[0], pt[1], inverse=True)
    return mercantile.tile(pt2[0],pt2[1], z)

bounds = []
bounds.append(dict(br=(-72,20), tl=(-129,49)))  # usa
bounds.append(dict(br=(-153.5,19.3), tl=(-160.3,21.9))) # hawaii
bounds.append(dict(br=(-128,55), tl=(170,52))) # alaska

tile_urls = []

for bbox in bounds:
    for z in range(min_z, max_z+1):
        tile_tl = get_tile(bbox['tl'][0], bbox['tl'][1], z)
        tile_br = get_tile(bbox['br'][0], bbox['br'][1], z)
        for x in range(tile_tl.x, tile_br.x+1):
            for y in range(tile_tl.y, tile_br.y+1):
                tile_urls.append('%d/%d/%d' % (z,x,y))

open('tile-urls.txt', 'w').write('\n'.join(tile_urls))