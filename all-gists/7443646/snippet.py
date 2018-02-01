#!/usr/bin/env python

# ndvi.py red.tif nir.tif output-ndvi.tif
# Calculate NDVI (see Wikipedia). Assumes atmospheric correction.
# (Although I use it without all the time for quick experiments.)

import numpy as np
from sys import argv
from osgeo import gdal, gdalconst

# Type for internal calculations:
t = np.float32

red, nir = map(gdal.Open, argv[1:3])

geotiff = gdal.GetDriverByName('GTiff')
output = geotiff.CreateCopy(argv[3], red, 0)

output = geotiff.Create(
   argv[3], 
   red.RasterXSize, red.RasterYSize, 
   1, 
   gdal.GDT_UInt16)

# Ugly syntax, but fast:
r = red.GetRasterBand(1).ReadAsArray(0, 0, red.RasterXSize, red.RasterYSize)
n = nir.GetRasterBand(1).ReadAsArray(0, 0, nir.RasterXSize, nir.RasterYSize)

# Convert the 16-bit Landsat 8 values to floats for the division operation:
r = r.astype(t)
n = n.astype(t)

# Tell numpy not to complain about division by 0:
np.seterr(invalid='ignore')

# Here's the meat of this whole thing, the actual NDVI formula:
ndvi = (n - r)/(n + r)

# The ndvi value is in the range -1..1, but we want it to be displayable, so:
# Make the value positive and scale it back up to the 16-bit range:
ndvi = (ndvi + 1) * (2**15 - 1)

# And do the type conversion back:
ndvi = ndvi.astype(np.uint16)

output.GetRasterBand(1).WriteArray(ndvi)