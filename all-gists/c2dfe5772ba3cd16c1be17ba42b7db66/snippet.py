# In Keras the Convolution layer requirest an additional dimension which will be used for the various filter.
# When we have eg. 2D dataset the shape is (data_points, rows, cols).
# But Convolution2D requires shape (data_points, rows, cols, 1).
# Otherwise it fails with eg. "Exception: Input 0 is incompatible with layer convolution2d_5: expected ndim=4, found ndim=3"
#
# Originally I reshaped the data beforehand but it only complicates things.
#
# An easier and more elegant solution is to add a Reshape layer at the input
# of the network!
#
# Docs: https://keras.io/layers/core/#reshape

from keras.models import Sequential, Model
from keras.layers import Input
from keras.layers.core import Activation, Reshape
from keras.layers.convolutional import Convolution2D

# eg. 100x100 px images
input_shape = (100, 100)

def create_model_sequential(input_shape):
  """For the classic sequential API..."""
  model = Sequential()

  # add one more dimension for convolution
  model.add(Reshape(input_shape + (1, ), input_shape=input_shape))

  model.add(Convolution2D(32, 3, 3))
  model.add(Activation('relu'))
  # ...

  return model

def create_model_functional(input_shape):
  """For the new functional API..."""
  inputs = Input(input_shape)

  # add one more dimension for convolution
  x = Reshape(input_shape + (1, ), input_shape=input_shape)(inputs)

  x = Convolution2D(32, 3, 3)(x)
  x = Activation('relu')(x)
  # ...

  return Model(inputs, x)