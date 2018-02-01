import numpy as np
import opensfm
import cv2
from opensfm import dataset
import pylab
import scipy.interpolate

import opensfm.features

def project(shot, point):
    p = shot.project(point.coordinates)
    return opensfm.features.denormalized_image_coordinates(
        p.reshape(1, 2), shot.camera.width, shot.camera.height)[0]


def warp_image(reconstruction, src_id, dst_id):
    src_shot = reconstruction.shots[src_id]
    dst_shot = reconstruction.shots[dst_id]
    points = reconstruction.points.values()
    src_points = np.array([project(src_shot, p) for p in points])
    dst_points = np.array([project(dst_shot, p) for p in points])
    src = data.image_as_array(src_id)
    dst = data.image_as_array(dst_id)
    dst_y, dst_x = np.indices(dst.shape[:2])
    dst_grid = np.column_stack([dst_x.ravel(), dst_y.ravel()])

    x = scipy.interpolate.griddata(dst_points, src_points[:, 0],
                                   dst_grid, method='linear')
    y = scipy.interpolate.griddata(dst_points, src_points[:, 1],
                                   dst_grid, method='linear')
    x = np.where(np.isnan(x), 0, x).reshape(dst.shape[:2])
    y = np.where(np.isnan(y), 0, y).reshape(dst.shape[:2])
    x = np.clip(x, 0, src.shape[1] - 1)
    y = np.clip(y, 0, src.shape[0] - 1)

    warped = src[y.astype(int), x.astype(int)]

    pylab.figure()
    pylab.subplot(2, 2, 1)
    pylab.title('source')
    pylab.imshow(src)
    pylab.subplot(2, 2, 2)
    pylab.title('target')
    pylab.imshow(dst)
    pylab.subplot(2, 2, 3)
    pylab.title('source wraped to target')
    pylab.imshow(warped)
    pylab.subplot(2, 2, 4)
    pylab.title('comparision')
    pylab.imshow(warped / 2 + dst / 2)


# load opensfm dataset
data = dataset.DataSet('/Users/eder/python/OpenSFM/data/berlin')
rec = data.load_reconstruction()[0]
print rec.shots['01.jpg']
shot = rec.shots['01.jpg']

for s in rec.shots.values():
    warp_image(rec, shot.id, s.id)

pylab.show()