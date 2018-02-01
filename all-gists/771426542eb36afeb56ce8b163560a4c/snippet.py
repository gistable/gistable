import numpy as np

import os
import glob
import cv2
import pandas as pd
import random

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten, Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Convolution2D, MaxPooling2D, \
                                       ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU, PReLU
from keras.regularizers import l2, activity_l2

from keras.callbacks import EarlyStopping
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD, Adam
from keras.utils import np_utils

# Global setting
np.random.seed(2016)

# color type: 1 - grey, 3 - rgb
color_type_global = 3

# resize image shape
img_rows, img_cols = 224, 224

# batch size and # of epoch
batch_size = 32

# Image data generator in keras
datagen = ImageDataGenerator(featurewise_center=False,
    samplewise_center=False,
    featurewise_std_normalization=False,
    samplewise_std_normalization=False,
    zca_whitening=False,
    rotation_range=13.,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    channel_shift_range=0.,
    fill_mode='nearest',
    cval=0.,
    horizontal_flip=False,
    vertical_flip=False,
    dim_ordering='th')


if os.path.exists(top_model_weights_path):
    os.remove(top_model_weights_path)

def show_image(im, name='image'):
    cv2.imshow(name, im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_im(path, img_rows, img_cols, color_type=1):
    # Load as grayscale
    if color_type == 1:
        img = cv2.imread(path, 0)
    elif color_type == 3:
        img = cv2.imread(path)
    # Reduce size
    resized = cv2.resize(img, (img_cols, img_rows))
    # mean_pixel = [103.939, 116.799, 123.68]
    #resized = resized.astype(np.float32, copy=False)

    # for c in range(3):
    #    resized[:, :, c] = resized[:, :, c] - mean_pixel[c]
    # resized = resized.transpose((2, 0, 1))
    # resized = np.expand_dims(img, axis=0)
    return resized

def process_line(img_list):
    target = int(img_list[1][1:])
    img_path = '../input/imgs/train/' + img_list[1] + '/' + img_list[2]
    img = get_im(img_path, img_rows, img_cols, color_type=color_type_global)
    return  img, target


def image_augmentation(X_train, Y_train, batch_size, datagen=datagen):

    datagen.fit(X_train)

    # fits the model on batches with real-time data augmentation:
    return datagen.flow(X_train, Y_train, batch_size=batch_size).next()


def generate_arrays_from_file(path, drivers_list=None, \
                        color_type=color_type_global, isvalidation=False, isfinetuning=False,\
                        finetuning_name=None, usingalldata=True):
    while 1:

        #print 'epoch'
        f = open(path)
        f.next() #columns
        #print f
        f_ = list(f)
        f.close()
        f = f_
        if isvalidation==False:
            random.shuffle(f)

        if isfinetuning == True:
            target_id = []

        batch_index = 0
        for line in f:
            if batch_index == 0:
                X_train = []
                y_train = []
            line = line.replace('\n', '').split(',')
            if usingalldata == True:
                if line[0] not in drivers_list:
                    continue
            # create numpy arrays of input data
            # and labels, from each line in the file
            #print line
            if isvalidation == False:
                x, y = process_line(line)
            else:
                x, y = process_line(line)

            if isfinetuning == True:
                target_id.append(y)

            X_train.append(x)
            y_train.append(y)
            batch_index += 1

            if batch_index % batch_size == 0:
                X_train = np.array(X_train, dtype=np.uint8)
                y_train = np.array(y_train, dtype=np.uint8)

                if color_type == 1:
                    X_train = X_train.reshape(X_train.shape[0], color_type,
                                                        img_rows, img_cols)
                else:
                    X_train = X_train.transpose((0, 3, 1, 2))

                y_train = np_utils.to_categorical(y_train, 10)
                X_train = X_train.astype('float32')

                if color_type == 1:
                    X_train /= 255

                else:
                    #X_train /= 255
                    mean_pixel = [103.939, 116.779, 123.68]
                    for c in range(3):
                        X_train[:, c, :, :] = X_train[:, c, :, :] - mean_pixel[c]

                if isvalidation == False:
                    X_train, y_train = image_augmentation(X_train, y_train, batch_index)

                #init
                batch_index = 0
                #print X_train
                yield (X_train, y_train)

        else:

            X_train = np.array(X_train, dtype=np.uint8)
            y_train = np.array(y_train, dtype=np.uint8)

            if color_type == 1:
                X_train = X_train.reshape(X_train.shape[0], color_type,
                                                            img_rows, img_cols)
            else:
                X_train = X_train.transpose((0, 3, 1, 2))

            y_train = np_utils.to_categorical(y_train, 10)
            X_train = X_train.astype('float32')

            if color_type == 1:
                X_train /= 255

            else:
                #X_train /= 255
                mean_pixel = [103.939, 116.779, 123.68]
                for c in range(3):
                    X_train[:, c, :, :] = X_train[:, c, :, :] - mean_pixel[c]

            if isvalidation == False:
                X_train, y_train = image_augmentation(X_train, y_train, batch_index)

            #init
            batch_index = 0

            if isfinetuning == True:
                target_id = np_utils.to_categorical(target_id, 10)
                np.save(open('target_{}.npy'.format(finetuning_name), 'w'), target_id)

            yield (X_train, y_train)

        # close file and shuffle data
        #f.close()


def test_prediction(data_path, color_type=color_type_global, batch_size = 64):

    """
    test_data_generator = test_prediction('../input/imgs/test/*.jpg')
    """
    print('Read test images')

    while 1:

        path = os.path.join(data_path)
        f = glob.glob(path)
        #for debug
        #f = f[:6000]
        X_test = []

        batch_index = 0
        for file_ in f:
            #X_test_id.append(os.path.basename(file_))

            if batch_index == 0:
                X_test = []
            #print line
            x = get_im(file_, img_rows, img_cols, color_type)

            X_test.append(x)
            batch_index += 1

            if batch_index % batch_size == 0:
                X_test = np.array(X_test, dtype=np.uint8)

                if color_type == 1:
                    X_test = X_test.reshape(X_test.shape[0], color_type,
                                                        img_rows, img_cols)
                else:
                    X_test = X_test.transpose((0, 3, 1, 2))

                X_test = X_test.astype('float32')

                if color_type == 1:
                    X_test /= 255

                else:
                    #X_test /= 255
                    mean_pixel = [103.939, 116.779, 123.68]
                    for c in range(3):
                        X_test[:, c, :, :] = X_test[:, c, :, :] - mean_pixel[c]

                #init
                batch_index = 0

                yield X_test

        else:
            X_test = np.array(X_test, dtype=np.uint8)

            if color_type == 1:
                X_test = X_test.reshape(X_test.shape[0], color_type,
                                                    img_rows, img_cols)
            else:
                X_test = X_test.transpose((0, 3, 1, 2))

            X_test = X_test.astype('float32')

            if color_type == 1:
                X_test /= 255

            else:
                #X_test /= 255
                mean_pixel = [103.939, 116.779, 123.68]
                for c in range(3):
                    X_test[:, c, :, :] = X_test[:, c, :, :] - mean_pixel[c]

            #init
            batch_index = 0

            yield X_test

def save_pred(preds, data_path, submission_name='submission'):
    print('Read test images name for submission file')
    path = os.path.join(data_path)
    f = glob.glob(path)
    X_test_id = []

    for file_ in f:
        X_test_id.append(os.path.basename(file_))

    preds_df = pd.DataFrame(preds, columns=['c0', 'c1', 'c2', 'c3',
                                 'c4', 'c5', 'c6', 'c7',
                                            'c8', 'c9'])
    preds_df['img'] = X_test_id

    print 'Saving predictions'
    preds_df.to_csv('submission/' + submission_name + '.csv', index=False)
    return

