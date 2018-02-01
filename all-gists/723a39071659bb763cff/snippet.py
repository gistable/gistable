"""
Author: Shubhanshu Mishra
Posted this on the keras issue tracker at: https://github.com/fchollet/keras/issues/108
Implementing a linear regression using Keras. 
"""

from keras.models import Sequential
from keras.layers.core import Dense, Activation

model = Sequential()
model.add(Dense(2,1,init='uniform', activation='linear'))
model.compile(loss='mse', optimizer='rmsprop')

model.fit(X_train, y_train, nb_epoch=1000, batch_size=16,verbose=0)
model.fit(X_train, y_train, nb_epoch=1, batch_size=16,verbose=1)
score = model.evaluate(X_test, y_test, batch_size=16)