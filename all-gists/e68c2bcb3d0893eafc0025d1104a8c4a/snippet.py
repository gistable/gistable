#!/usr/bin/env python3

import sys
from scipy.io import wavfile
from numpy import *
from pylab import *

'''Voice ranges for male 'M' and female 'M' humans, those gave us 98.9 accuracy
from given samples'''
M = (60, 180)
F = (160, 270)

def hps(signal, frequency, n=5):
    '''
    HPS method for a given signal sample with a certain frequency
    The default number of iterations is 5, can be changed via the optional
    parameter n.
    Returns a vector of frequencies values len(signal)/n wide.
    Since addition accumulates a lot of noise in lower frequencies (circa 40Hz)
    we use multiplication which implies there must be 5 nearly perfect
    harmonics in the sample.
    '''
    window_size = len(signal)
    signal = signal * hamming(window_size)  # hamming window to smooth out
    transformed = abs(fft(signal, window_size))/frequency  # normalization
    short = copy(transformed)
    for i in range(2, n + 1):  # take every n-th sample
        x = copy(transformed[::i])
        short = short[:len(x)]
        short *= x
    return short


def sex_detector(filename, window_size=2**14, n=5, window_span=10):
    '''
    Given a single-channeled .wav file filename,
    return a single letter 'K' or 'M' if the voice
    is detected as a female or male
    '''
    frequency, signal = wavfile.read(filename)
    length = len(signal)
    '''overlap is how much we divide the window the the smaller overlap the
    faster but less acurate the method will be'''
    overlap = 8

    results = []
    windows = range(max(0, length//2 - window_span*window_size),
                    min(length - 1, length//2 + window_span*window_size),
                    window_size//overlap)
    '''
    We take out samples from the middle of the signal (length//2).
    We then run hps over window_span number of samples left and right,
    overlapping by window_size/overlap elements.
    '''
    results = [hps(signal[i:i+window_size], frequency, n=n) for i in windows]

    x = linspace(0, frequency, window_size, endpoint=False)[:len(results[0])]
    results = [element for element in results if len(element) == len(x)]
    results = sum(results, axis=0)

    '''Best way to determine way is sum parts of the signals between
    male/female frequencies '''
    male = sum([res for f, res in zip(x, results) if f >= M[0] and f <= M[1]])
    fem = sum([res for f, res in zip(x, results) if f >= F[0] and f <= F[1]])

    return 'K' if fem > male else 'M'


if __name__ == '__main__':
    print(sex_detector(sys.argv[1]))
