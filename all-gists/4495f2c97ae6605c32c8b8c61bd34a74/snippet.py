import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import Adam
from keras.utils import np_utils
from sklearn import metrics 

# to run this code, you'll need to load the following data: 
# train_x, train_y
# valid_x, valid_y
# test_x, test_y
# see http://aqibsaeed.github.io/2016-09-24-urban-sound-classification-part-2/ for details

# data dimension parameters 
frames = 41
bands = 60
num_channels = 2
num_labels = test_y.shape[1]

# start by creating a linear stack of layers
model = Sequential()

# will use filters of size 2x2 
f_size = 2

# first layer applies 32 convolution filters 
# input: 60x41 data frames with 2 channels => (60,41,2) tensors
model.add(Convolution2D(32, f_size, f_size, border_mode='same', input_shape=(bands, frames, num_channels)))
model.add(Activation('relu'))
model.add(Convolution2D(32, f_size, f_size))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.15))

# next layer applies 64 convolution filters
model.add(Convolution2D(64, f_size, f_size, border_mode='same'))
model.add(Activation('relu'))
model.add(Convolution2D(64, f_size, f_size))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

# flatten output into a single dimension 
# Keras will do the shape inference automatically
model.add(Flatten())

# then a fully connected NN layer
model.add(Dense(256))
model.add(Activation('relu'))
model.add(Dropout(0.5))

# finally, an output layer with one node per class
model.add(Dense(num_labels))
model.add(Activation('softmax'))

# use the Adam optimiser
adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)

# now compile the model, Keras will take care of the Tensorflow boilerplate
model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer=adam)

# for quicker training, just using one epoch, you can experiment with more
model.fit(train_x, train_y, validation_data=(valid_x, valid_y), batch_size=32, nb_epoch=1)

# finally, evaluate the model using the withheld test dataset

# determine the ROC AUC score 
y_prob = model.predict_proba(test_x, verbose=0)
y_pred = np_utils.probas_to_classes(y_prob)
y_true = np.argmax(test_y, 1)
roc = metrics.roc_auc_score(test_y, y_prob)
print "ROC:", round(roc,3)

# determine the classification accuracy
score, accuracy = model.evaluate(test_x, test_y, batch_size=32)
print("\nAccuracy = {:.2f}".format(accuracy))