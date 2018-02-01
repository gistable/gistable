import matplotlib,numpy
import pylab
# A random colormap for matplotlib
cmap = matplotlib.colors.ListedColormap ( numpy.random.rand ( 256,3))
pylab.imshow ( Z, cmap = cmap)
pylab.show()