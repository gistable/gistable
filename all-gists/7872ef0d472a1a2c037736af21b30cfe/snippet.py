# Tutorial from: http://bit.ly/2olREnv
import numpy
from keras.datasets import cifar10
from matplotlib import pyplot
from scipy.misc import toimage
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.constraints import maxnorm
from keras.optimizers import SGD
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K

########################################
# Example: Simple CNN model for CIFAR-10

# Set the column/row order
K.set_image_dim_ordering('th')

# load CFAIR-10 data
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# create a 3x3 grid plot of random images
for i in range(0, 9):
    for j in numpy.random.choice(len(X_train), 9).tolist():
        pyplot.subplot(330 + 1 + i)
        pyplot.imshow(toimage(X_train[j]))
pyplot.show()

# fix random seed for reproducibility
seed = 9
numpy.random.seed(seed)

# normalize inputs from 0-255 to 0.0-1.0
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train = X_train / 255.0
X_test = X_test / 255.0

# One hot encode outputs
y_train = np_utils.to_categorical(y_train)
y_test = np_utils.to_categorical(y_test)
num_classes = y_test.shape[1]

# Create the model
model = Sequential()
# Create 32 3x3 filters to move across the image, pad the image (border_mode),
# throw away negatives (activation), max weight is 3 (W_c)
# model.add(Convolution2D(32, 3, 3,
#                         input_shape=(3, 32, 32),
#                         border_mode='same',
#                         activation='relu',
#                         W_constraint=maxnorm(3)))
model.add(Conv2D(32, (3, 3),
                 activation="relu",
                 input_shape=(3, 32, 32),
                 padding="same",
                 kernel_constraint=maxnorm(3)))
# Randomly throw away 20% of the filters
model.add(Dropout(0.2))
# Take the last layer and convolute again
# model.add(Convolution2D(32, 3, 3,
#                         activation='relu',
#                         border_mode='same',
#                         W_constraint=maxnorm(3))
model.add(Conv2D(32, (3, 3),
                 activation="relu",
                 padding="same",
                 kernel_constraint=maxnorm(3)))
# Reduce resolution by taking the max value of a 2x2 across the image.
model.add(MaxPooling2D(pool_size=(2, 2)))
# Make a 1D vector ~8K here
model.add(Flatten())
# Fully Conneted Layer (dense) 8kx512 (multiply output by fully connected
# layer (Wx+b)
# model.add(Dense(512, activation='relu', W_constraint=maxnorm(3)))
model.add(Dense(512, activation='relu', kernel_constraint=maxnorm(3)))
# Throw away 1/2
model.add(Dropout(0.5))
# Always last layer, fit to one hot vector
model.add(Dense(num_classes, activation='softmax'))

# Compile model
epochs = 25
lrate = 0.01
decay = lrate / epochs
# Specify back prop method (Stochastic Gradiant Decent)
sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
# Loss says how do i know how well I'm doing
model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])
print(model.summary())

# Fit the model
model.fit(X_train,
          y_train,
          validation_data=(X_test, y_test),
          epochs=epochs,
          batch_size=32)
# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1] * 100))

##################################################
# Larger Convolutional Neural Network for CIFAR-10

# Create the model
model = Sequential()
model.add(Conv2D(32, (3, 3),
                 input_shape=(3, 32, 32),
                 activation='relu',
                 border_mode='same'))
model.add(Dropout(0.2))
model.add(Conv2D(32, (3, 3), activation='relu', border_mode='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu', border_mode='same'))
model.add(Dropout(0.2))
model.add(Conv2D(64, (3, 3), activation='relu', border_mode='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu', border_mode='same'))
model.add(Dropout(0.2))
model.add(Conv2D(128, (3, 3), activation='relu', border_mode='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dropout(0.2))
model.add(Dense(1024, activation='relu', W_constraint=maxnorm(3)))
model.add(Dropout(0.2))
model.add(Dense(512, activation='relu', W_constraint=maxnorm(3)))
model.add(Dropout(0.2))
model.add(Dense(num_classes, activation='softmax'))
# Compile model
epochs = 25
lrate = 0.01
decay = lrate / epochs
sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
model.compile(loss='categorical_crossentropy',
              optimizer=sgd, metrics=['accuracy'])
print(model.summary())

numpy.random.seed(seed)
model.fit(X_train, y_train,
          validation_data=(X_test, y_test), nb_epoch=epochs, batch_size=64)
# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
print("Deep accuracy: %.2f%%" % (scores[1] * 100))
