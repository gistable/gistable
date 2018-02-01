#!/usr/bin/env python
"""Demonstrate Keras model weight shuffling as fast alternative to re-creating a model."""

from __future__ import print_function

import numpy as np
from keras.layers import Dense
from keras.models import Sequential


def shuffle_weights(model, weights=None):
    """Randomly permute the weights in `model`, or the given `weights`.

    This is a fast approximation of re-initializing the weights of a model.

    Assumes weights are distributed independently of the dimensions of the weight tensors
      (i.e., the weights have the same distribution along each dimension).

    :param Model model: Modify the weights of the given model.
    :param list(ndarray) weights: The model's weights will be replaced by a random permutation of these weights.
      If `None`, permute the model's current weights.
    """
    if weights is None:
        weights = model.get_weights()
    weights = [np.random.permutation(w.flat).reshape(w.shape) for w in weights]
    # Faster, but less random: only permutes along the first dimension
    # weights = [np.random.permutation(w) for w in weights]
    model.set_weights(weights)


def main():
    """Train a simple single layer to learn the sum of three inputs.
    Shuffle weights in a mock "cross-validation" loop instead of re-creating the model to save time.
    """
    np.random.seed(42)
    model = Sequential((
        Dense(input_dim=3, output_dim=1, activation='linear'),
    ))
    model.compile(loss='msle', optimizer='rmsprop')

    X = np.random.random(size=(1000, 3))
    y = np.sum(X, axis=1)

    initial_weights = model.get_weights()
    print('Initial weights:\n', initial_weights)

    for rnd in xrange(3):
        shuffle_weights(model, initial_weights)
        print('\nRound {} starting weights:\n'.format(rnd), model.get_weights())
        hist = model.fit(X, y, nb_epoch=50, verbose=0)
        print('Learned weights:\n', model.get_weights(), '\nloss:', hist.history['loss'][-1])


if __name__ == '__main__':
    main()
