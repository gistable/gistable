from sys import argv
from shapely.ops import polygonize
from shapely.geometry import asShape, LineString

import json

if __name__ == '__main__':

    input = argv[1]
    input = json.load(open(input))
    lines = []
    
    for feat in input['features']:
        shape = asShape(feat['geometry'])
        geoms = hasattr(shape, 'geoms') and shape.geoms or [shape]
        
        for part in geoms:
            coords = list(part.coords)
            for (start, end) in zip(coords[:-1], coords[1:]):
                lines.append(LineString([start, end]))
    
    areas = polygonize(lines)
    output = dict(type='FeatureCollection', features=[])
    
    for (index, area) in enumerate(areas):
        
        feature = dict(type='Feature', properties=dict(index=index))
        feature['geometry'] = area.__geo_interface__
        output['features'].append(feature)
    
    json.dump(output, open(argv[2], 'w'))
