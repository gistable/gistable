
from pylab import *
from scipy.stats import beta, norm, uniform
from random import random
from numpy import *
import numpy as np
import os

# Input data
prior_params = [ (1, 1), (1,1) ]
threshold_of_caring = 0.001

N = array([ 100, 104 ])
s = array([ 13, 8 ])

#N = [ 581, 583 ]
#s = [ 112, 75 ]

class ABTest(object):
    def finish_test_index(self, data):
        # return index of when test is finished
        pass

    def finish_test_value(self, index, cumsum):
        # return 0 or 1
        pass

def gen_data(ctr, size=1024*2):
    ctr = array(ctr)
    rnd = uniform(0,1).rvs((2,size))
    data = zeros(shape=(2,size))
    data[where(rnd < ctr[:,newaxis])] = 1.0
    return data

def evaluate_test_procedure(ctr, data, proc):
    ctr = array(ctr)
    n = proc.finish_test_index(data)
    choice = proc.finish_test_value(N=(n,n), s=sum(data[:,0:n-1], axis=1))
    lift = ctr[choice] - ctr[1-choice]
    return (n, lift)


class ComputesNormalDistPValue(object):
    def p_value(self, N, s):
        empirical_ctr = s.astype(float) / N
        std_error = sqrt(empirical_ctr[0]*(1.0-empirical_ctr[0])/N[0] + (empirical_ctr[1]*(1-empirical_ctr[1]))/N[1])
        if (std_error == 0):
            return 1
        z_value = (empirical_ctr[1]-empirical_ctr[0])/std_error
        p_value = 1 - norm().cdf(abs(z_value))
        return p_value

class GaussianFrequentistPValue(ABTest, ComputesNormalDistPValue):
    def __init__(self, sample_size, cutoff):
        self.sample_size = sample_size
        self.cutoff = cutoff

    def __str__(self):
        return "GaussianFrequentistPValue(" + str(self.sample_size) + ", " + str(self.cutoff) + ")"

    def finish_test_index(self, data):
        return self.sample_size

    def finish_test_value(self, N, s):
        empirical_ctr = s.astype(float) / N
        pv = self.p_value(N,s)
        if (pv <= self.cutoff) and (empirical_ctr[1] > empirical_ctr[0]):
            return 1
        else:
            return 0

class BayesianBetaAB(ABTest):
    def __init__(self, prior, threshold_of_caring, stride=25):
        self.prior = prior
        self.threshold_of_caring = threshold_of_caring
        self.xgrid_size = 1024*2
        self.stride = stride
        self.x = mgrid[0:self.xgrid_size,0:self.xgrid_size] / float(self.xgrid_size)
        self.x_1d = arange(0,1,1.0/self.xgrid_size)
        #Precompute to avoid unnecessary work
        self.loss = [maximum(self.x[0]-self.x[1],0.0), maximum(self.x[1]-self.x[0],0.0)]
        # Pre-allocate to avoid GC
        self.pdf = zeros(shape=(self.xgrid_size,self.xgrid_size), dtype=float)
        self.work_arr = zeros(shape=(self.xgrid_size,self.xgrid_size), dtype=float) #Where loss * pdf is stored

    def __str__(self):
        return "BayesianBeta(" + str(self.prior) + ", " + str(self.threshold_of_caring) + ")"

    def finish_test_value(self, N, s):
        empirical_ctr = s.astype(float) / N
        if s[1] > s[0]:
            return 1
        else:
            return 0

    def finish_test_index(self, data):
        s = array([0,0]).astype(float)
        old_n = 0
        sa = np.cumsum(data, axis=1)
        for n in range(self.stride,data.shape[1],self.stride):
            N = array([n,n])
            s = sa[:,n]
            old_n = n
            empirical_ctr = s.astype(float) / N.astype(float)
            posteriors = []
            for i in range(2):
                posteriors.append(beta(self.prior[0] + s[i] - 1, self.prior[1] + N[i] - s[i] - 1))
            self.pdf[:] = 1.0
            self.pdf[:] *= posteriors[0].pdf(self.x_1d)[newaxis,:]
            self.pdf[:] *= posteriors[1].pdf(self.x_1d)[:,newaxis]
            # The above 3 lines should be equivalent to (posteriors[0].pdf(self.x[0]) * posteriors[1].pdf(self.x[1]))

            #print "delta: " + str(((posteriors[0].pdf(self.x[0]) * posteriors[1].pdf(self.x[1])) - self.pdf).sum())
            #self.pdf[:] = posteriors[0].pdf(self.x[0]) * posteriors[1].pdf(self.x[1])

            # Normalize at end
            # self.pdf[:] /= self.pdf.sum() #We don't normalize until computing expected_loss as performance hack
            if (empirical_ctr[0] > empirical_ctr[1]):
                loss = self.loss[0]
            else:
                loss = self.loss[1]
            self.work_arr[:] = 0.0
            self.work_arr[:] = loss[:]
            self.work_arr[:] *= self.pdf
            expected_loss = (self.work_arr).sum() / self.pdf.sum()
            if (expected_loss < self.threshold_of_caring):
                return n
        return n

procedures = [BayesianBetaAB( (1,1), 0.01),
              BayesianBetaAB( (1,1), 0.005),
              BayesianBetaAB( (1,1), 0.001),
              BayesianBetaAB( (1,1), 0.0001),
              GaussianFrequentistPValue(500, 0.1),
              GaussianFrequentistPValue(1000, 0.1),
              GaussianFrequentistPValue(1500, 0.1),
              GaussianFrequentistPValue(2000, 0.1),
              GaussianFrequentistPValue(4000, 0.1),
              GaussianFrequentistPValue(500, 0.05),
              GaussianFrequentistPValue(1000, 0.05),
              GaussianFrequentistPValue(1500, 0.05),
              GaussianFrequentistPValue(2000, 0.05),
              GaussianFrequentistPValue(4000, 0.05),
              GaussianFrequentistPValue(500, 0.01),
              GaussianFrequentistPValue(1000, 0.01),
              GaussianFrequentistPValue(2000, 0.01),
              GaussianFrequentistPValue(4000, 0.01),
              ]

procedure_lift = zeros(shape=(len(procedures),), dtype=float)
procedure_samples = zeros(shape=(len(procedures),), dtype=float)
ctr_dist = beta(0.5, 50)
#ctr_dist = beta(5, 100)

def print_table(oracle_lift, procedure_lift, procedure_samples, n):
    print "<table>"
    print "<tr><th>Method</th><th>Samples</th><th>Lift</th></tr>"
    for j in range(len(procedure_samples)):
        print "<tr><td>" + str(procedures[j]) + "</td><td>" + str(int(procedure_samples[j] / float(n))) + "</td><td>" + str((procedure_lift[j] / float(n)) / oracle_lift) + "</td></tr>"
    print "</table>"


num_tests = 250

absolute_lift = 0.0
for i in range(num_tests):
    ctr = ctr_dist.rvs(2)
    absolute_lift += abs(ctr[1]-ctr[0])
    data = gen_data(ctr, size=1024*4)
    print "Outer iteration: " + str(i) + ", ctr="+str(ctr)
    for (j, proc) in enumerate(procedures):
        nsamples, lift = evaluate_test_procedure(ctr, data, proc)
        procedure_lift[j] += lift
        procedure_samples[j] += nsamples
    if (i % 10 == 0) and (i > 0):
        oracle_lift = absolute_lift / float(i)
        print_table(oracle_lift, procedure_lift, procedure_samples, i+1)

oracle_lift = absolute_lift / float(num_tests)
print_table(oracle_lift, procedure_lift, procedure_samples, num_tests)
