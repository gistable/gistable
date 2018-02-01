from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

# Plotting 2070 projected August (8) precip from worldclim
gdata = gdal.Open("D:/jon/datasets/worldclim/future/pr/gf45pr70_usa/gf45pr708.tif")
geo = gdata.GetGeoTransform()
data = gdata.ReadAsArray()

xres = geo[1]
yres = geo[5]

# A good LCC projection for USA plots
m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)

# This just plots the shapefile -- it has already been clipped
m.readshapefile('D:/jon/datasets/USGS HUCs/US_states/states','states',drawbounds=True, color='0.3')

xmin = geo[0] + xres * 0.5
xmax = geo[0] + (xres * gdata.RasterXSize) - xres * 0.5
ymin = geo[3] + (yres * gdata.RasterYSize) + yres * 0.5
ymax = geo[3] - yres * 0.5

x,y = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]
x,y = m(x,y)

cmap = plt.cm.gist_rainbow
cmap.set_under ('1.0')
cmap.set_bad('0.8')

im = m.pcolormesh(x,y, data.T, cmap=cmap, vmin=0, vmax=100)

cb = plt.colorbar( orientation='vertical', fraction=0.10, shrink=0.7)
plt.title('August Precip (mm)')
plt.show()
