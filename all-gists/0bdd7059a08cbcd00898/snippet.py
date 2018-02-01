"""
Possibly correct implementation of an all conv neural network using a single residual module

This code was written for instruction purposes and no attempt to get the best results were made.

References:
Deep Residual Learning for Image Recognition: http://arxiv.org/pdf/1512.03385v1.pdf
STRIVING FOR SIMPLICITY, THE ALL CONVOLUTIONAL NET: http://arxiv.org/pdf/1412.6806v3.pdf

A video walking through the code and main ideas: https://youtu.be/-N_zlfKo4Ec
"""

from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Graph
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, AveragePooling2D
from keras.utils import np_utils

batch_size = 128
nb_classes = 10
nb_epoch = 12

# input image dimensions
img_rows, img_cols = 28, 28
# number of convolutional filters to use
nb_filters = 64
# size of pooling area for max pooling
nb_pool = 2
# convolution kernel size
nb_conv = 3

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()

X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

####################################################
# Define Model
####################################################
model = Graph()

model.add_input(input_shape=(1, 28, 28), name="0")

# first piece
model.add_node(Convolution2D(
        nb_filters, nb_conv, nb_conv, input_shape=(1, img_rows, img_cols), activation="relu"), name="1", input="0")
model.add_node(Convolution2D(
        nb_filters, nb_conv, nb_conv, activation="relu"), name="2", input="1")
model.add_node(Convolution2D(
        nb_filters, nb_conv, nb_conv, subsample=(2, 2), activation="relu"), name="X", input="2")
        
model.compile(loss={"out": 'categorical_crossentropy'}, optimizer='adam')
model.fit({"0": X_train, "out": Y_train}, nb_epoch=5, show_accuracy=True)

# residual module
# batch_norm
model.add_node(Convolution2D(nb_filters, nb_conv, nb_conv,
                             activation="relu", border_mode="same"), name="r1", input="X")
# batch_norm
model.add_node(Convolution2D(nb_filters, nb_conv, nb_conv,
                             activation="relu", border_mode="same"), name="r2", input="r1")

# add layer_3 + residual_module
model.add_node(Convolution2D(
        nb_filters, nb_conv, nb_conv, subsample=(2, 2), activation="relu"),
        name="3", inputs=["X", "r2"], merge_mode="sum")

# classifier
model.add_node(Convolution2D(10, nb_conv, nb_conv, activation="linear"), name="4", input="3")

out_size = model.nodes["4"].output_shape[-1]  # thanks shape inference
model.add_node(AveragePooling2D((out_size, out_size)),
               name="pool", input="4")
model.add_node(Flatten(), name="flat", input="pool")
model.add_node(Activation("softmax"), name="out", input="flat", create_output=True)