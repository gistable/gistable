#!/usr/bin/env python

from numpy import asmatrix, asarray, ones, zeros, mean, sum, arange, prod, dot, loadtxt
from numpy.random import random, randint
import pickle

MISSING_VALUE = -1 # a constant I will use to denote missing integer values

def impute_hidden_node(E, I, theta, sample_hidden):

    theta_T, theta_E = theta

    # calculate the unnormalized probability associated with the hidden unit being a 0
    theta_E_wide = asarray( ones([E.shape[0],1]) * asmatrix(theta_E[:,0]) )
    p_vis_0 = I * (theta_E_wide * E + (1-theta_E_wide) * (1-E)) + (I==0)*1
    prob_0_unnorm = (1-theta_T) * prod(p_vis_0, 1)

    # calculate the unnormalized probability associated with the hidden unit being a 1
    theta_E_wide = asarray( ones([E.shape[0],1]) * asmatrix(theta_E[:,1]) )
    p_vis_1 = I * (theta_E_wide * E + (1-theta_E_wide) * (1-E)) + (I==0)*1
    prob_1_unnorm = theta_T * prod(p_vis_1, 1)

    hidden = prob_1_unnorm / (prob_0_unnorm + prob_1_unnorm)

    if sample_hidden:
        # set the hidden unit to a 0 or 1 instead of a probability of activation
        hidden = (hidden > random( hidden.shape ))*1

    return hidden

def simulate(theta, nsamples):

    theta_T, theta_E = theta
    
    T = (theta_T > random(nsamples))

    # (multiplying by T selects the cases where T=1, multiplying by 1-T selects the cases where T=0)
    E = (asmatrix(1-T).transpose() * theta_E[:,0] > random([nsamples, theta_E.shape[0]]))  \
      + (asmatrix(T).transpose() * theta_E[:,1] > random([nsamples, theta_E.shape[0]]))

    E = asarray(E * 1)

    return T, E

def compute_theta(T, E):
    
    theta_T = mean(T) # the probability is the average activation
    theta_E = zeros([E.shape[1], 2]) 

    for e in range(E.shape[1]):
        E_col = E[:,e] 
        ix = E_col != MISSING_VALUE  # row indices that are not missing this evidence
        theta_E[e,0] = sum( E_col[ix] * (1-T[ix]) ) / float( sum( 1-T[ix] ) ) # the average of E when T=0
        theta_E[e,1] = sum( E_col[ix] * T[ix] ) / float( sum( T[ix] ) ) # the average of E when T=1

    return [theta_T, theta_E]

def print_theta(theta):

    theta_T, theta_E = theta
    
    print "T\t0: %f\t1:%f" % (1-theta_T, theta_T)
    for i in range( theta_E.shape[0] ):
        print "E%d T=0\t0: %f\t1:%f" % (i, 1-theta_E[i,0], theta_E[i,0])
        print "E%d T=1\t0: %f\t1:%f" % (i, 1-theta_E[i,1], theta_E[i,1])

def learn(T, E, max_iter, sample_hidden):
    
    I = (E!=MISSING_VALUE)*1  #indicator matrix on whether evidence for each E-variable is present
    
    theta = compute_theta( T,E ) 

    for i in range(max_iter):
        T = impute_hidden_node(E, I, theta, sample_hidden)  # E-step

        # there are two equivalent solutions with T=0 and T=1 flipped.  always take the solution where T=1 is more probable.
        if mean(T) < 0.5:
            T = 1-T

        theta = compute_theta( T, E )    # M-step

        print "Run %d produced theta of:" % i
        print_theta(theta) 
        #log_likelihood(data, theta)
    return theta


def simulated_example():

    # start by specifying a TRUE joint distribution, theta.
    theta_T = 0.75 # probability that T is 1
    theta_E = asarray(zeros( [5, 2] )) # probability that E is 1.  [number of leaves] x [number of T states]
    theta_E[0,0] = 0.55 # probability that E0 = 1 if T = 0 
    theta_E[0,1] = 0.95 # probability that E0 = 1 if T = 1
    theta_E[1,0] = 0.60 # probability that E1 = 1 if T = 0
    theta_E[1,1] = 0.95 # probability that E1 = 1 if T = 1
    theta_E[2,0] = 0.24 # probability that E2 = 1 if T = 0
    theta_E[2,1] = 0.42 # probability that E2 = 1 if T = 1
    theta_E[3,0] = 0.13 # probability that E3 = 1 if T = 0
    theta_E[3,1] = 0.72 # probability that E3 = 1 if T = 1
    theta_E[4,0] = 0.62 # probability that E4 = 1 if T = 0
    theta_E[4,1] = 0.66 # probability that E4 = 1 if T = 1
    theta = [theta_T, theta_E]
    
    # now generate/simulate a dataset accoriding to theta 
    row_count = 10000;  print "rowcount = %d" % row_count
    [T, E] = simulate(theta, row_count)
    
    # randomize/hide the 'T' variable, to see if we can re-learn it
    T2 = T.copy()
    T = randint(2, size=row_count)
    
    # in addition, randomly remove between 1 to 3 E-values for each sample as 'missing' data
    for i in range(0):
        E[arange(row_count), randint(5,size=row_count)] = MISSING_VALUE
    
    # finally, try to learn the parameters 
    theta_learned = learn(T, E, 400, sample_hidden=True)
    
    print 'Starting State:'
    print_theta(compute_theta(T,E))
    print 'Ending State:'
    print_theta(theta_learned)
    print 'Goal:'
    print_theta(theta)

def ka_data_example():
    E = loadtxt('bnet.csv', dtype=int, delimiter=',', skiprows=1)
    T = randint(2, size=E.shape[0])

    theta_learned = learn(T, E, 200, sample_hidden=True)

    print 'Starting State:'
    print_theta(compute_theta(T,E))
    print 'Ending State:'
    print_theta(theta_learned)

    pickle.dump([theta_learned[0], theta_learned[1].tolist()], open('theta.pickle', 'wb'))
    
if __name__ == '__main__':
    simulated_example()
    ka_data_example()