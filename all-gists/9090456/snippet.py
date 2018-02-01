from matplotlib import use

from pylab import *
from scipy.stats import beta, norm, uniform
from random import random
from numpy import *
import numpy as np
import os

# Input data
prior_params = [ (1, 1), (1,1) ]
threshold_of_caring = 0.001

N = array([ 200, 204 ])
s = array([ 16, 36 ])

#Don't edit anything past here

def bayesian_expected_error(N,s):
    degrees_of_freedom = len(prior_params)
    posteriors = []
    for i in range(degrees_of_freedom):
        posteriors.append( beta(prior_params[i][0] + s[i] - 1, prior_params[i][1] + N[i] - s[i] - 1) )
    xgrid_size = 1024
    x = mgrid[0:xgrid_size,0:xgrid_size] / float(xgrid_size)
    # Compute joint posterior, which is a product distribution
    pdf_arr = posteriors[0].pdf(x[1]) * posteriors[1].pdf(x[0])
    pdf_arr /= pdf_arr.sum() # normalization
    expected_error_dist = maximum(x[0]-x[1],0.0) * pdf_arr
    return expected_error_dist.sum()

# Code
degrees_of_freedom = len(prior_params)
posteriors = []
for i in range(degrees_of_freedom):
    posteriors.append( beta(prior_params[i][0] + s[i] - 1, prior_params[i][1] + N[i] - s[i] - 1) )

if degrees_of_freedom == 2:
    xgrid_size = 1024

    x = mgrid[0:xgrid_size,0:xgrid_size] / float(xgrid_size)
    # Compute joint posterior, which is a product distribution
    pdf_arr = posteriors[0].pdf(x[1]) * posteriors[1].pdf(x[0])
    pdf_arr /= pdf_arr.sum() # normalization

    prob_error = zeros(shape=x[0].shape)
    if (s[1] / float(N[1])) > (s[0] / float(N[0])):
        prob_error[where(x[1] > x[0])] = 1.0
    else:
        prob_error[where(x[0] > x[1])] = 1.0

    expected_error = maximum(abs(x[0]-x[1]),0.0)

    expected_err_scalar = (expected_error * prob_error * pdf_arr).sum()

    if (expected_err_scalar < threshold_of_caring):
        if (s[1] / float(N[1])) > (s[0] / float(N[0])):
            print "Probability that version B is larger is " + str((prob_error*pdf_arr).sum())
            print "Terminate test. Choose version B. Expected error is " + str(expected_err_scalar)
        else:
            print "Probability that version A is larger is " + str((prob_error*pdf_arr).sum())
            print "Terminate test. Choose version A. Expected error is " + str(expected_err_scalar)
    else:
        print "Probability that version B is larger is " + str((prob_error*pdf_arr).sum())
        print "Continue test. Expected error was " + str(expected_err_scalar) + " > " + str(threshold_of_caring)
