""" From:  http://danielhnyk.cz/predicting-sequences-vectors-keras-using-rnn-lstm/ """
from keras.models import Sequential  
from keras.layers.core import TimeDistributedDense, Activation, Dropout  
from keras.layers.recurrent import GRU
import numpy as np

def _load_data(data, steps = 40):  
    docX, docY = [], []
    for i in range(0, data.shape[0]/steps-1):
        docX.append(data[i*steps:(i+1)*steps,:])
        docY.append(data[(i*steps+1):((i+1)*steps+1),:])
    alsX = np.array(docX)
    alsY = np.array(docY)
    return alsX, alsY

def train_test_split(data, test_size=0.15):  
    #    This just splits data to training and testing parts
    X,Y = _load_data(data)
    ntrn = round(X.shape[0] * (1 - test_size))
    perms = np.random.permutation(X.shape[0])
    X_train, Y_train = X.take(perms[0:ntrn],axis=0), Y.take(perms[0:ntrn],axis=0)
    X_test, Y_test = X.take(perms[ntrn:],axis=0),Y.take(perms[ntrn:],axis=0)
    return (X_train, Y_train), (X_test, Y_test) 

np.random.seed(0)  # For reproducability
data = np.genfromtxt('closingAdjLog.csv', delimiter=',')
(X_train, y_train), (X_test, y_test) = train_test_split(np.flipud(data))  # retrieve data
print "Data loaded."

in_out_neurons = 20  
hidden_neurons = 200

model = Sequential()  
model.add(GRU(hidden_neurons, input_dim=in_out_neurons, return_sequences=True))
model.add(Dropout(0.2))
model.add(TimeDistributedDense(in_out_neurons))  
model.add(Activation("linear"))  
model.compile(loss="mean_squared_error", optimizer="rmsprop") 
print "Model compiled."

# and now train the model. 
model.fit(X_train, y_train, batch_size=30, nb_epoch=200, validation_split=0.1)  
predicted = model.predict(X_test)  
print np.sqrt(((predicted - y_test) ** 2).mean(axis=0)).mean()  # Printing RMSE 