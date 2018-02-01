from __future__ import print_function

import os

import numpy as np
from keras.layers import RepeatVector
from keras.layers.core import Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model

np.random.seed(123)


def prepare_sequences(x_train, window_length, random_indices):
    full_sequence = x_train.flatten()
    windows = []
    outliers = []
    for window_start in range(0, len(full_sequence) - window_length + 1):
        window_end = window_start + window_length
        window_range = range(window_start, window_end)
        window = list(full_sequence[window_range])
        contain_outlier = len(set(window_range).intersection(set(random_indices))) > 0
        outliers.append(contain_outlier)
        windows.append(window)
    return np.expand_dims(np.array(windows), axis=2), outliers


def get_signal(size, outliers_size=0.01):
    sig = np.expand_dims(np.random.normal(loc=0, scale=1, size=(size, 1)), axis=1)
    if outliers_size < 1:  # percentage.
        outliers_size = int(size * outliers_size)
    random_indices = np.random.choice(range(size), size=outliers_size, replace=False)
    sig[random_indices] = np.random.randint(6, 9, 1)[0]
    return sig, random_indices


def tp_fn_fp_tn(total, expected, actual):
    tp = len(set(expected).intersection(set(actual)))
    fn = len(set(expected) - set(actual))
    fp = len(set(actual) - set(expected))
    tn = len((total - set(expected)).intersection(total - set(actual)))
    return tp, fn, fp, tn


def main():
    window_length = 10
    select_only_last_state = False
    model_file = 'model.h5'
    hidden_dim = 16

    # no outliers.
    signal_train, _ = get_signal(100000, outliers_size=0)
    x_train, _ = prepare_sequences(signal_train, window_length, [])

    # 1 percent are outliers.
    signal_test, random_indices = get_signal(100000, outliers_size=0.01)
    x_test, contain_outliers = prepare_sequences(signal_test, window_length, random_indices)
    outlier_indices = np.where(contain_outliers)[0]

    if os.path.isfile(model_file):
        m = load_model(model_file)
    else:
        m = Sequential()
        if select_only_last_state:
            m.add(LSTM(hidden_dim, input_shape=(window_length, 1), return_sequences=False))
            m.add(RepeatVector(window_length))
        else:
            m.add(LSTM(hidden_dim, input_shape=(window_length, 1), return_sequences=True))
        m.add(Dropout(p=0.1))
        m.add(LSTM(1, return_sequences=True, activation='linear'))
        m.compile(loss='mse', optimizer='adam')
        m.fit(x_train, x_train, batch_size=64, nb_epoch=5, validation_data=(x_test, x_test))
        m.save(model_file)

    pred_x_test = m.predict(x_test)
    mae_of_predictions = np.squeeze(np.max(np.square(pred_x_test - x_test), axis=1))
    mae_threshold = np.mean(mae_of_predictions) + np.std(mae_of_predictions)  # can use a running mean instead.
    actual = np.where(mae_of_predictions > mae_threshold)[0]

    tp, fn, fp, tn = tp_fn_fp_tn(set(range(len(pred_x_test))), outlier_indices, actual)
    precision = float(tp) / (tp + fp)
    hit_rate = float(tp) / (tp + fn)
    accuracy = float(tp + tn) / (tp + tn + fp + fn)

    print('precision = {}, hit_rate = {}, accuracy = {}'.format(precision, hit_rate, accuracy))


if __name__ == '__main__':
    main()
