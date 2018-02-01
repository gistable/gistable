#!/usr/bin/env python

"""
Author: Jeremy M. Stober
Program: RARGMAX.PY
Date: Wednesday, February 29 2012
Description: Simple rargmax function.
"""

import numpy as np
import random as pr

def rargmax(vector):
    """ Argmax that chooses randomly among eligible maximum indices. """
    m = np.amax(vector)
    indices = np.nonzero(vector == m)[0]
    return pr.choice(indices)

if __name__ == '__main__':
    test = [0,1,2,2]
    for i in range(10):
        print rargmax(test)
