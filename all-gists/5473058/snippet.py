from matplotlib import pylab # .exe install is on sourceforge
import numpy# easy_install numpy
from mpl_toolkits.basemap import Basemap # easy_install basemap

# functions to create some random data points and convert them to meters via the map projection
def create_points_in_lon_lat(N=10000):
    return zip(numpy.random.standard_normal(N)*360, numpy.random.standard_normal(N) * 45)

def convert_lon_lat_points_to_meters_using_transform(points, tran):
    # maybe there is a better way to get long/lat into meters but this works ok
    return numpy.array([tran(long,lat) for long,lat in points])

# creates an object called map which can plot various things on different projections
map = Basemap(llcrnrlon=-90,llcrnrlat=-90,urcrnrlon=270,urcrnrlat=90,projection='mill')

# get random points in meters
points = convert_lon_lat_points_to_meters_using_transform(create_points_in_lon_lat(), map.projtran)

# draw the hexbin
# points[:,i]: selects all rows but just the ith column - used to turn
# list or long,lat pairs into lists of just long and lat but in the same order.
# gridsize: set the number of hexagons in the x and y dimension
# mincnt: set the minimum count in a hexagon for it to be drawn
# cmap: set the colour map to use
map.hexbin(points[:,0],points[:,1], gridsize=(200,30),mincnt=1,cmap=pylab.cm.Purples)

# draw some features - the basemap object come with these build in but you can load
# features in from a wide range of formats
map.drawcoastlines()

# show the resulting plot in the interactive viewer (waits till figure is closed before continuing)
pylab.show()
# or you could save it directly to a file like this:
#pylab.savefig('hexbintestmap.png')
# see also:
# http://matplotlib.org/basemap/users/examples.html