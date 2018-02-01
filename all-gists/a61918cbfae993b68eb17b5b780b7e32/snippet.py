import numpy as np
import pandas as pd
from math import sqrt

from keras.models import Sequential
from keras.layers.core import Dense, Activation

from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler

from sklearn.cross_validation import train_test_split

from keras.regularizers import l2, activity_l2
from keras.layers.advanced_activations import ParametricSoftplus

import pickle

#data is from https://www.crowdanalytix.com/contests/predict-fuel-flow-rate-of-airplanes-during-different-phases-of-a-flight
# A Pandas dataframe where y column is FF and X columns are every other column except for 
# Flight instance ID and ACID (also an id field).
training_data = pd.read_pickle('Training_files/PH_data_one.df')

feature_columns = [col for col in training_data.columns if not (col=='FF' or col=='Flight_instance_ID' or  col=='ACID')]

y = training_data['FF'].values
X = training_data[feature_columns].values

X = StandardScaler().fit(X).transform(X)
X = VarianceThreshold(threshold=0.0).fit_transform(X)

#split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)
model = Sequential()

#https://github.com/fchollet/keras/issues/108
model.add(Dense(60,  input_dim=177, W_regularizer=l2(0.05), activity_regularizer=activity_l2(0.01)))
model.add(Activation('tanh'))
model.add(Dense(24, W_regularizer=l2(0.1), activity_regularizer=activity_l2(0.01)))
model.add(Activation('tanh'))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='rmsprop')

model.fit(X_train, y_train, nb_epoch=240, batch_size=16, verbose=1)

#if you want to save the model for later use
#pickle.dump(model, open("linear_keras.model", "wb" ))

score = model.evaluate(X_test, y_test, batch_size=16)

print "RMSE " + str(sqrt(score))