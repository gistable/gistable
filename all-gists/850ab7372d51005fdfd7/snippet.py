# python pca_multiband.py input.jpeg output.tif
# n-band image -> PCA -> n-band TIFF image
# with lots of hackety assumptions
# (e.g., output is same type as input)

from sys import argv
import rasterio as rio
import numpy as np
from sklearn import decomposition

with rio.open(argv[1]) as src:
  meta = src.meta
  pixels = src.read()
  
dtype = meta['dtype']
count = meta['count']
  
# Todo: make this cleaner:
pixels = np.dstack([c.ravel() for c in pixels])[0]

pca = decomposition.PCA(n_components=count, whiten=False)
pca.fit(pixels)

for band in range(len(pca.components_)):
  print(
    'Band {0} will hold {1:.4g} of variance with weights:\n{2}'.format(
      band+1,
      pca.explained_variance_ratio_[band],
      ', '.join("{0:.4g}".format(x) for x in pca.components_[band])))
      # .format() within .format()! Wow! Very pro move, very well
      # respected technique, 9.7 even from the East German judges!

# Here's the actual work:
out = pca.transform(pixels)

# This is the messy reverse of the messy ravel above:
xyz = np.array([
  out[:,c].reshape(meta['height'], meta['width'])
  for c in range(count)
])

# Scale each band separately to fill out the data type.
# (You either really want this or really don't want this.)
xyz = np.array([
  ((c - np.amin(c))/(np.amax(c) - np.amin(c)))*np.iinfo(dtype).max
  for c in xyz
])

xyz = xyz.astype(dtype)

meta.update({
  'transform': meta['affine'],
  'driver': 'GTiff'
})

with rio.open(argv[2], 'w', **meta) as dst:
  dst.write(xyz)