#!/usr/bin/env python
# Takes an interger n for 2^n x 2^n Hadamard matrix

import numpy as np
import sys

def recursiveKronecker(k, hmat):
    if 2**(k-1) == 1:
        return hmat
    else:
        return np.kron(hmat, recursiveKronecker(k-1, hmat))

def main():
    np.set_printoptions(threshold='nan') # Print matrix objects without abbr 
    n = sys.argv[1]

    if not n.isdigit():
        print 'n must be int'
        quit()
    else:
        n = int(n)

    # 2x2 Hadamard matrix
    h2 = np.matrix([[1,1],[1,-1]])

    print 'H_%d = '%2**n
    print recursiveKronecker(n, h2)  

if __name__ == "__main__":
    main()