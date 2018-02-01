import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import fiona

df = pd.read_csv('data.csv')

geometry = [Point(xy) for xy in zip(df.x, df.y)]
crs = {'init': 'epsg:2263'} #http://www.spatialreference.org/ref/epsg/2263/
geo_df = GeoDataFrame(df, crs=crs, geometry=geometry)

geo_df.to_file(driver='ESRI Shapefile', filename='data.shp')



# https://gis.stackexchange.com/questions/204201/geopandas-to-file-saves-geodataframe-without-coordinate-system
# http://geopandas.org/io.html#writing-spatial-data
# https://gis.stackexchange.com/questions/174159/convert-a-pandas-dataframe-to-a-geodataframe