#install keras from https://github.com/kundajelab/keras/tree/keras_1
from __future__ import print_function
import keras
import numpy as np
np.random.seed(1)

#build a model
model = keras.models.Sequential()
model.add(keras.layers.convolutional.Convolution1D(input_shape=(1000,4),
                                                   nb_filter=300,
                                                   filter_length=19))
model.add(keras.layers.normalization.BatchNormalization())
model.add(keras.layers.core.Activation("relu"))
model.add(keras.layers.pooling.MaxPooling1D(pool_length=3, stride=3))

model.add(keras.layers.convolutional.Convolution1D(nb_filter=200,
                                                   filter_length=11))
model.add(keras.layers.normalization.BatchNormalization())
model.add(keras.layers.core.Activation("relu"))
model.add(keras.layers.pooling.MaxPooling1D(pool_length=4, stride=4))

model.add(keras.layers.convolutional.Convolution1D(nb_filter=200,
                                                   filter_length=7))
model.add(keras.layers.normalization.BatchNormalization())
model.add(keras.layers.core.Activation("relu"))
model.add(keras.layers.pooling.MaxPooling1D(pool_length=4, stride=4))


model.add(keras.layers.convolutional.SeparableFC(symmetric=True,
                                                 smoothness_second_diff=True,
                                                 output_dim=1000,
                                                 smoothness_penalty=10.0,
                                                 smoothness_l1=True))

model.add(keras.layers.core.Dense(output_dim=1000))
model.add(keras.layers.core.Activation("relu"))
model.add(keras.layers.core.Dropout(0.3))

model.add(keras.layers.core.Dense(output_dim=1000))
model.add(keras.layers.core.Activation("relu"))
model.add(keras.layers.core.Dropout(0.3))

model.add(keras.layers.core.Dense(output_dim=10))
model.add(keras.layers.core.Activation("sigmoid"))
model.compile(optimizer="Adam", loss="binary_crossentropy")

#randomly generate some inputs and get predictions
rand_inp = np.random.random((10, 1000, 4))
predict = model.predict(rand_inp)