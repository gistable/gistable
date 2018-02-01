#! /usr/bin/env python
"""
Author: Jeremy M. Stober
Program: SOFTMAX.PY
Date: Wednesday, February 29 2012
Description: Simple softmax function.
"""

import numpy as np
npa = np.array

def softmax(w, t = 1.0):
    e = np.exp(npa(w) / t)
    dist = e / np.sum(e)
    return dist

if __name__ == '__main__':

    w = np.array([0.1,0.2])
    print softmax(w)

    w = np.array([-0.1,0.2])
    print softmax(w)

    w = np.array([0.9,-10])
    print softmax(w)
