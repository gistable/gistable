from multiprocessing import Pool
import sys
import fiona
from fiona.transform import transform_geom
from shapely.geometry import mapping, shape
import json

def reproject(f, srs_crs, dest_crs):
    f['geometry'] = transform_geom(srs_crs, dest_crs, f['geometry'],
                          antimeridian_cutting=True,
                          precision=-1)
    return f

def buffer(f, v):
    f['geometry'] = mapping(shape(f['geometry']).buffer(v))
    return f

class Process:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __call__(self, f):
        return reproject(buffer(reproject(f, self.crs, 'EPSG:3857'), 1E+5), 'EPSG:3857', 'EPSG:4326')

if __name__ == '__main__':
    pool = Pool()
    with fiona.open(sys.argv[1], 'r') as source:
        p = Process(crs=source.crs)
        res = pool.map(p, source)
    print json.dumps({
        'type': 'FeatureCollection',
        'features': res
    })