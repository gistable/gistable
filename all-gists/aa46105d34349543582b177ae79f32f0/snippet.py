# -*- coding: utf-8 -*-

import h5py
import os
import numpy as np
from random import shuffle
import shutil
from PIL import Image

SIZE = 227
TEST_IMAGE = False
TEST_READ_H5 = False
TEST_ONE_BATCH = False
AVOID_WRITING_HDF5 = False

PIXEL_MEANS = np.array([123, 117, 104]).reshape((1, 1, 3))  # ImageNET channel-wise means
TARGET_DIMENSION = 2
HDF5_DIR = 'hdf5/'


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def show_image(img):
    from skimage.viewer import ImageViewer
    img = img.transpose((1, 2, 0))
    img = img[:, :, ::-1]
    viewer = ImageViewer(img.reshape(SIZE, SIZE, 3))
    viewer.show()


def go():
    if not AVOID_WRITING_HDF5 and not TEST_IMAGE and not TEST_READ_H5:
        recreate_dir(HDF5_DIR)
    with open('labels.txt') as label_file:
        f_idx = 0
        all_lines = label_file.readlines()
        if TEST_ONE_BATCH:
            chunk_size = 1
        else:
            chunk_size = 1000
            shuffle(all_lines)
        for lines in chunker(all_lines, chunk_size):
            print('starting f_idx: ' + str(f_idx))
            images = np.zeros((len(lines), 3, SIZE, SIZE), dtype='u4')
            targets = np.zeros((len(lines), TARGET_DIMENSION), dtype='f4')
            for i, line in enumerate(lines):
                image_name, speed, speed_change, steer, direction = line.split(' ')
                img = np.array(Image.open('images/' + image_name))
                # img -= PIXEL_MEANS  # Subtract the pixel-wise mean
                img = img[:, :, ::-1]  # RGB => BGR
                img = img.transpose((2, 0, 1))  # in Channel x Height x Width order (switch from H x W x C)
                images[i] = img
                if TEST_IMAGE:
                    show_image(img)
                target = [steer, speed]
                targets[i] = target
            if not AVOID_WRITING_HDF5:
                output_h5(f_idx, images, targets)
            f_idx += 1
            if TEST_ONE_BATCH:
                break


def output_h5(f_idx, images, targets):
    h5_filename = HDF5_DIR + 'train_' + str(f_idx).zfill(4) + '.h5'
    print('writing hdf5 file for f_idx: ' + str(f_idx))
    with h5py.File(h5_filename, 'w') as H:
        H.create_dataset('images', data=images)
        H.create_dataset('targets', data=targets)
    if TEST_READ_H5:
        with h5py.File(h5_filename, 'r') as hf:
            images_test = hf.get('images')
            targets_test = hf.get('targets')
            for i, img in enumerate(images_test):
                print(targets_test[i])
                show_image(img)


def recreate_dir(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)


go()
