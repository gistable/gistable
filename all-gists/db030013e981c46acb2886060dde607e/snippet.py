from __future__ import division
from functools import partial

import pyproj
from shapely.ops import transform
import numpy as np

from rasterio import features
from affine import Affine
import fiona

import datashader as ds
from datashader.colors import Hot, viridis
import pdb
from datashader import transfer_functions as tf
from xarray import DataArray
from multiprocessing import Pool

def rasterize_geom(cvs, geom, all_touched=False, fill=0):
    aform = Affine((cvs.x_range[1] - cvs.x_range[0]) / cvs.plot_width,
                   0.0,
                   cvs.x_range[0],
                   0.0, (cvs.y_range[0] - cvs.y_range[1]) / cvs.plot_height, cvs.y_range[1])
    rv_array = features.rasterize(((geom, 1)),
                                  out_shape=(cvs.plot_height, cvs.plot_width),
                                  transform=aform,
                                  fill=fill,
                                  all_touched=all_touched)
    return rv_array

def main():
    shp = 'MAMMALS.shp'
    cvs = ds.Canvas(plot_height=2000,
                    plot_width=4000,
                    x_range=(-180, 180),
                    y_range=(-90, 90))

    out_arr = None
    count = 0
    problems = 0
    with fiona.collection(shp, "r") as source:
        for feat in source:
            try:
                r = rasterize_geom(cvs, feat['geometry'])
                if out_arr is None:
                    out_arr = r
                else:
                    out_arr += r
                count += 1
                print(count)
            except:
                print('problem...')
                problems += 1
                continue

    img = tf.interpolate(DataArray(data=np.flipud(out_arr)),
                                   cmap=viridis,
                                   how='linear')
    tf.set_background(img, 'black').to_pil().save("mammals_linear.png")
    print('Count: {}'.format(count))
    print('Problems: {}'.format(problems))

if __name__ == '__main__':
    main()