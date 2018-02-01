#!/usr/bin/env python

#http://geoinformaticstutorial.blogspot.it/2012/09/reading-raster-data-with-python-and-gdal.html
#http://www.gis.usu.edu/~chrisg/python/2009/lectures/ospy_slides4.pdf

from osgeo import gdal,ogr
from osgeo.gdalconst import *
import struct
import sys

lon = 12.502742
lat = 42.243713

lat = float(sys.argv[2])
lon = float(sys.argv[3])

def pt2fmt(pt):
	fmttypes = {
		GDT_Byte: 'B',
		GDT_Int16: 'h',
		GDT_UInt16: 'H',
		GDT_Int32: 'i',
		GDT_UInt32: 'I',
		GDT_Float32: 'f',
		GDT_Float64: 'f'
		}
	return fmttypes.get(pt, 'x')

ds = gdal.Open(sys.argv[1], GA_ReadOnly)
if ds is None:
	print 'Failed open file'
	sys.exit(1)

transf = ds.GetGeoTransform()
cols = ds.RasterXSize
rows = ds.RasterYSize
bands = ds.RasterCount #1
band = ds.GetRasterBand(1)
bandtype = gdal.GetDataTypeName(band.DataType) #Int16
driver = ds.GetDriver().LongName #'GeoTIFF'

success, transfInv = gdal.InvGeoTransform(transf)
if not success:
	print "Failed InvGeoTransform()"
	sys.exit(1)

px, py = gdal.ApplyGeoTransform(transfInv, lon, lat)

structval = band.ReadRaster(int(px), int(py), 1,1, buf_type = band.DataType )

fmt = pt2fmt(band.DataType)

intval = struct.unpack(fmt , structval)

print round(intval[0],2) #intval is a tuple, length=1 as we only asked for 1 pixel value

