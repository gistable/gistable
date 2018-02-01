from keras.models import Sequential
from keras.layers import Dense
from keras.utils.io_utils import HDF5Matrix
import numpy as np

def create_dataset():
    import h5py
    X = np.random.randn(200,10).astype('float32')
    y = np.random.randint(0, 2, size=(200,1))
    f = h5py.File('test.h5', 'w')
    # Creating dataset to store features
    X_dset = f.create_dataset('my_data', (200,10), dtype='f')
    X_dset[:] = X
    # Creating dataset to store labels
    y_dset = f.create_dataset('my_labels', (200,1), dtype='i')
    y_dset[:] = y
    f.close()

create_dataset()

# Instantiating HDF5Matrix for the training set, which is a slice of the first 150 elements
X_train = HDF5Matrix('test.h5', 'my_data', start=0, end=150)
y_train = HDF5Matrix('test.h5', 'my_labels', start=0, end=150)

# Likewise for the test set
X_test = HDF5Matrix('test.h5', 'my_data', start=150, end=200)
y_test = HDF5Matrix('test.h5', 'my_labels', start=150, end=200)

# HDF5Matrix behave more or less like Numpy matrices with regards to indexing
print(y_train[10])
# But they do not support negative indices, so don't try print(X_train[-1])

model = Sequential()
model.add(Dense(64, input_shape=(10,), activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='sgd')

# Note: you have to use shuffle='batch' or False with HDF5Matrix
model.fit(X_train, y_train, batch_size=32, shuffle='batch')

model.evaluate(X_test, y_test, batch_size=32)
