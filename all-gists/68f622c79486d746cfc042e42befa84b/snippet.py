import json
from shapely.geometry import Polygon, shape, Point
import gdal
import numpy as np
import sys
fn = sys.argv[1]
path = sys.argv[2]

def Pixel2World ( geoMatrix, i , j ):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    return(1.0 * i * xDist  + ulX, -1.0 * j * xDist + ulY)
ds8 = gdal.Open(path+'8band/'+'8band_'+fn+'.tif')
ds3 = gdal.Open(path+'3band/'+'3band_'+fn+'.tif')
geoTrans = ds8.GetGeoTransform()
with open(path + 'vectorData/geoJson/'+fn+'_Geo.geojson','r') as f:
    js = json.load(f)
    dist = np.zeros((ds8.RasterXSize, ds8.RasterYSize))
    for i in range(ds8.RasterXSize):
        for j in range(ds8.RasterYSize):
            point = Point(Pixel2World( geoTrans, i , j ))
            pd = -100000.0
            for feature in js['features']:
                polygon = shape(feature['geometry'])
                newpd = point.distance(polygon.boundary)
                 if False == polygon.contains(point):
                     newpd = -1.0 * newpd
                 if newpd > pd :
                     pd = newpd
             dist[i,j] = pd
np.save(path+'CosmiQ_distance/'+fn+'.distance',dist)