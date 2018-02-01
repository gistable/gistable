import os
import sys
import numpy as np
from data_util import *
import datetime

ply_filelist = 'scripts/modelnet40_ply_filelist_shuffled.txt'

H5_BATCH_SIZE = 2000

shape_names = get_category_names()
shape_name_dict = {shape_names[i]: i for i in range(len(shape_names))}

def filename_to_class_label(filename):
    shape_name = filename.split('/')[-2]
    return shape_name_dict[shape_name]

def main():
    ply_filenames = [line.rstrip() for line in open(ply_filelist)]
    labels = [filename_to_class_label(fn) for fn in ply_filenames]

    N = len(labels)

    data_dim = [SAMPLING_POINT_NUM, 3]
    label_dim = [1]
    data_dtype = 'float32'
    label_dtype = 'uint8'

    output_dir = os.path.join(BASE_DIR, 'data', 'modelnet40_ply_0930', 'ply_data_hdf5')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_filename_prefix = os.path.join(output_dir, 'ply_data')

    batch_data_dim = [min(H5_BATCH_SIZE, N)] + data_dim
    batch_label_dim = [min(H5_BATCH_SIZE, N)] + label_dim

    h5_batch_data = np.zeros(batch_data_dim, dtype = np.float32)
    h5_batch_label = np.zeros(batch_label_dim, dtype = np.uint8)
    
    print h5_batch_data.shape
    print h5_batch_label.shape

    def unit_test(batch_num):
        h5_filename = output_filename_prefix + '_' + str(batch_num) + '.h5'
        print 'Performing unit test for hdf5 file %s' % h5_filename
        d, l = load_h5(h5_filename)
        print 'data shape: ', d.shape
        print 'label shape: ', l.shape
        print 'label diff: %f' % np.linalg.norm(l.T - labels[batch_num*H5_BATCH_SIZE: min((batch_num+1)*H5_BATCH_SIZE, N)])

    for k in range(N):
        if k % 100 == 0:
            print 'Iteration %d/%d' % (k, N)
        d = load_ply_data(ply_filenames[k])
        d = pad_arr_rows(d, row=SAMPLING_POINT_NUM)
        l = labels[k]
        h5_batch_data[k%H5_BATCH_SIZE, ...] = d
        h5_batch_label[k%H5_BATCH_SIZE, ...] = l

        if (k+1)%H5_BATCH_SIZE == 0 or k == N - 1:
            print '[%s] %d/%d' % (datetime.datetime.now(), k+1, N)
            h5_filename = output_filename_prefix + '_' + str(k/H5_BATCH_SIZE) + '.h5'
            begidx = 0
            endidx = k % H5_BATCH_SIZE + 1
            save_h5(h5_filename, h5_batch_data[begidx:endidx, ...], 
                    h5_batch_label[begidx:endidx, ...], 
                    data_dtype, label_dtype)
            print 'Stored %d objects' % (endidx - begidx)

            unit_test(k/H5_BATCH_SIZE)

main()