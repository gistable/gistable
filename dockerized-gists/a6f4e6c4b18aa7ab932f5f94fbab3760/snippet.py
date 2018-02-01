#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
Do you have some "outlier" noise in your experimental data, e.g. due to "hot pixels" in spectrometer?

Run

    python3 rm_outliers.py my_file.dat

and the new "my_file.dat_corrected.dat" will be free of these errors.
"""

import numpy as np

x,y = np.loadtxt(sys.argv[1], unpack=True)
kernel = [1,0,1] # averaging of neighbors #kernel = np.exp(-np.linspace(-2,2,5)**2) ## Gaussian
kernel /= np.sum(kernel)                        # normalize
smooth = np.convolve(y, kernel, mode='same')    # find the average value of neighbors
rms_noise = np.average((y[1:]-y[:-1])**2)**.5   # estimate what the average noise is (rms derivative)
where_not_excess =  (np.abs(y-smooth) < rms_noise*3)    # find all points with difference from average less than 3sigma
x,y = x[where_not_excess],y[where_not_excess]   # filter the data

np.savetxt(sys.argv[1]+"_corrected.dat", np.array([]).T)