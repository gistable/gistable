import geopandas as gpd
import numpy as np
import requests
import gdal
import fiona
import uuid  
import re

# informaed by: https://gis.stackexchange.com/questions/225586/reading-raw-data-into-geopandas/225627

def shapefilereader(target):
    """Function to convert zipped shapefiles from the web or on disk into geopandas dataframes
    
    Parameters
    ----------
    target : str
        string representing path to file on disk or url to download the zipped shapefile.
    
    Returns
    -------
    Geopandas dataframe
        Pandas dataframe with geospatial features and operations.
    
    """
    
    # Detect whether we are using a web-based shapefile or local disk
    r = re.compile('^(http|https)://',re.I)
    if r.search(target):
        download = True
        request = requests.get(target)
        target = '/vsimem/{}.zip'.format(uuid.uuid4().hex) #gdal/ogr requires a .zip extension
        gdal.FileFromMemBuffer(target,bytes(request.content))
    else:
        download = False
    
    
    with fiona.Collection(target,vsi='zip') as f:
        return gpd.GeoDataFrame.from_features(f,crs=f.crs)