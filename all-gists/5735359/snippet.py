from PIL import Image
import numpy
from skimage.filter import sobel
from skimage.morphology import watershed
from scipy import ndimage as nd

grind = numpy.asarray(Image.open('grind.png')).mean(axis=2)

edges = sobel(grind)
markers = numpy.zeros_like(grind)

# Grind is dark on white background (paper)
markers[grind < 70] = 1
markers[grind > 150] = 2

labels, num_features = nd.label(markers == 1)

areas = []
for i in xrange(num_features):
    total = (labels == i).sum()
    if total < 4 or total > 1000:
        continue
    areas.append(total)

print "mean {:.2f}".format(numpy.array(areas).mean())
