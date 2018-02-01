import keras
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.wrappers.scikit_learn import KerasClassifier

import numpy as np


def target2classes(y):
    y_2class = np.zeros((y.shape[0],2))
    y_2class[y==0, 0] = 1
    y_2class[y==1, 1] = 1
    return y_2class


# Data generation
np.random.seed(1337)
X = np.random.rand(88737, 245)
X = (X-X.mean(axis=0))/X.std(axis=0)
y = np.random.binomial(1, 1.0/2500, size=(88737,))


# Model definition
model = Sequential()

model.add(Dense(2000, input_dim=245, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.2))

model.add(Dense(2000, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.2))

model.add(Dense(600, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.2))

model.add(Dense(2, init='uniform'))
model.add(Activation('sigmoid'))

rmsprop = keras.optimizers.RMSprop(lr=0.00001, rho=0.9, epsilon=1e-6)


# Training
y_ohe = target2classes(y)
inverse_frequencies = float(y_ohe.sum())/y_ohe.sum(axis=0)
class_weight = dict((i, inverse_freq) for i, inverse_freq in enumerate(inverse_frequencies))

model.compile(loss='binary_crossentropy',
                      optimizer=rmsprop)

model.fit(X, y_ohe, batch_size=256,
                      nb_epoch=1,
                      class_weight=class_weight,
                      verbose=1)
