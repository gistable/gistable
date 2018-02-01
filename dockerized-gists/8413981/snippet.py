#!/usr/bin/env python
# encoding: utf-8

import numpy as np


def Cp(mylist, usl, lsl):
    arr = np.array(mylist)
    arr = arr.ravel()
    sigma = np.std(arr)
    Cp = float(usl - lsl) / (6*sigma)
    return Cp


def Cpk(mylist, usl, lsl):
    arr = np.array(mylist)
    arr = arr.ravel()
    sigma = np.std(arr)
    m = np.mean(arr)

    Cpu = float(usl - m) / (3*sigma)
    Cpl = float(m - lsl) / (3*sigma)
    Cpk = np.min([Cpu, Cpl])
    return Cpk


if __name__ == "__main__":
    #a1 = np.random.randn(10)
    #print a1
    #print Cp(a1, 1, -1)
    #print Cpk(a1, 1, -1)

    a1 = np.arange(0, 10)
    print a1
    print Cp(a1, 10, 0)
    print Cpk(a1, 10, 0)