'''Trains a simple convnet on the MNIST dataset.
Does flat increment from T. Xiao  "Error-Driven Incremental Learning in Deep Convolutional 
Neural Network for Large-Scale Image Classification"
Starts with just 3 classes, trains for 12 epochs then 
incrementally trains the rest of the classes by reusing 
the trained weights.
'''

from __future__ import print_function
import numpy as np
np.random.seed(1)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential, model_from_json
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.utils import np_utils

def build_data(classes,total_classes,X_train_all,y_train_all,X_test_all,y_test_all):
    train_ind = []
    test_ind = []
    for c in classes:
        train_ind.extend(list(np.where(y_train_all==c)[0]))
        test_ind.extend(list(np.where(y_test_all==c)[0]))

    X_train = X_train_all[train_ind,:,:]
    X_test = X_test_all[test_ind,:,:]

    y_train_true = y_train_all[train_ind]
    y_train = np.zeros(y_train_true.shape)
    y_test_true = y_test_all[test_ind]
    y_test = np.zeros(y_test_true.shape)

    for i,c in enumerate(classes):
        train_ind = list(np.where(y_train_true==c)[0])
        test_ind = list(np.where(y_test_true==c)[0])
        y_train[train_ind] = i
        y_test[test_ind] = i


    X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
    X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255

    # convert class vectors to binary class matrices
    Y_train = np_utils.to_categorical(y_train, total_classes)
    Y_test = np_utils.to_categorical(y_test, total_classes)
    
    return X_train, Y_train, X_test, Y_test

def build_model(old_model=None):
    model = Sequential()

    if old_model is None:
        model.add(Convolution2D(nb_filters, nb_conv, nb_conv,
                        border_mode='valid',
                        input_shape=(1, img_rows, img_cols)))
    else:
        weights = old_model.layers[0].get_weights()
        model.add(Convolution2D(nb_filters, nb_conv, nb_conv,
                        border_mode='valid',weights=weights,
                        input_shape=(1, img_rows, img_cols)))
    model.add(Activation('relu'))
    if old_model is None:
        model.add(Convolution2D(nb_filters, nb_conv, nb_conv))
    else:
        weights = old_model.layers[2].get_weights()
        model.add(Convolution2D(nb_filters, nb_conv, nb_conv,weights=weights))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(nb_pool, nb_pool)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    if old_model is None:
        model.add(Dense(128))
    else:
        weights = old_model.layers[7].get_weights()
        model.add(Dense(128,weights=weights))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    return model

if __name__ == '__main__':
    MODEL_TRAINED = False
    # input image dimensions
    img_rows, img_cols = 28, 28

    # the data, shuffled and split between train and test sets
    (X_train_all, y_train_all), (X_test_all, y_test_all) = mnist.load_data()

    if not MODEL_TRAINED:
        batch_size = 256
        total_classes = 10
        nb_epoch = 12

        # number of convolutional filters to use
        nb_filters = 32
        # size of pooling area for max pooling
        nb_pool = 2
        # convolution kernel size
        nb_conv = 3

        classes = [9,1,6]
        X_train, Y_train, X_test, Y_test = build_data(classes,3,
                                                      X_train_all,y_train_all,X_test_all,y_test_all)

        model1 = build_model()
        model1.add(Dense(len(classes)))
        model1.add(Activation('softmax'))
        model1.compile(loss='categorical_crossentropy',optimizer='adadelta',metrics=['accuracy'])

        model1.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epoch,
                   verbose=1, validation_data=(X_test, Y_test))

        # Save this model for later interrogation
        json_string = model1.to_json() 
        open('model1_incremental_architecture.json', 'w').write(json_string) 
        model1.save_weights('model1_incremental_weights.h5') 

        score = model1.evaluate(X_test, Y_test, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

        # Now create a new model with all total_classes in the softmax layer.  Copy over the weights to
        # this new network and initialize the new class connections randomly.
        model2 = build_model(old_model=model1)
        model2.add(Dense(total_classes))

        # Replace the corresponding weights of the new network with the previously trained class weights
        weights = model2.layers[-1].get_weights()
        old_weights = model1.layers[-2].get_weights() # Last dense layer is second to last layer
        weights[0][:,-len(classes):] = old_weights[0]
        weights[1][-len(classes):] = old_weights[1]
        model2.layers[-1].set_weights(weights)
        model2.add(Activation('softmax'))
        model2.compile(loss='categorical_crossentropy',optimizer='adadelta',metrics=['accuracy'])
    
        new_classes = [7, 0, 3, 5, 2, 8, 4]
        class_mapping = new_classes[:]
        class_mapping.extend(classes)
        X_train, Y_train, X_test, Y_test = build_data(new_classes,10,
                                                      X_train_all,y_train_all,X_test_all,y_test_all)
    
        model2.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epoch,
                   verbose=1, validation_data=(X_test, Y_test))
        score = model2.evaluate(X_test, Y_test, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])
    
        # Save the incrementally trained model
        json_string = model2.to_json() 
        open('model2_incremental_architecture.json', 'w').write(json_string) 
        model2.save_weights('model2_incremental_weights.h5') 

        X_test = X_test_all.reshape(X_test_all.shape[0], 1, img_rows, img_cols)
        X_test = X_test.astype('float32')
        X_test /= 255

        # Convert class vectors to binary class matrices
        # Note, that when a new image is presented to this network, the label of the image must be 
        # fed into class_mapping to get the "real" label of the output
        y_test = np.array([class_mapping.index(c) for c in y_test_all])
        Y_test = np_utils.to_categorical(y_test, total_classes)

        score = model2.evaluate(X_test, Y_test, verbose=1)
        print('Total Test score:', score[0])
        print('Total Test accuracy:', score[1])

    else:    
        # Load the incrementally trained model and test it 
        model = model_from_json(open('model2_incremental_architecture.json').read()) 
        model.load_weights('model2_incremental_weights.h5')
        model.compile(loss='categorical_crossentropy',optimizer='adadelta',metrics=['accuracy'])

        classes = [7, 0, 3, 5, 2, 8, 4, 9, 1, 6]
        X_train, Y_train, X_test, Y_test = build_data(classes,10,
                                                      X_train_all,y_train_all,X_test_all,y_test_all)

        score = model.evaluate(X_test, Y_test, verbose=1)
        print('Total Test score:', score[0])
        print('Total Test accuracy:', score[1])

        score = model.evaluate(X_train, Y_train, verbose=1)
        print('Total Train score:', score[0])
        print('Total Train accuracy:', score[1])
