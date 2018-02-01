#!/usr/bin/env python

from pandas import DataFrame, Series

import numpy as np
import math
import random
import copy

NaN_Flag = -1  # pandas uses np.nan, but that coerces ints to floats :(

def print_theta(theta):
    for node, cpt in theta.iteritems():
        for key in cpt:
            print "%s\t'%s'\t%s" % (node, key, cpt[key])

def parents(node, adj):
    result = []
    for col in adj.columns:
        if adj.ix[node, col]==1:
            result.append(col)
    return result

def parent_map(adj):
    return dict( [(col,parents(col,adj)) for col in adj.columns] )

def children(node, adj):
    result = []
    for candidate in nodes:
        if candidate==node:
            continue
        if node in parents(candidate, adj):
            result.append(candidate)
    return result

def draw(pdt):
    r = random.random()
    cumulative_prob = 0.0
    for (val, prob) in pdt.iteritems():
        cumulative_prob += prob
        if r < cumulative_prob:
            return val

def simulate(adj, theta, num_samples):
    data = DataFrame.from_items( [(node, Series(np.zeros(num_samples, int))) for node in adj.columns] )
    for node in adj.columns: 
        P = parents(node, adj) 
        for n in range(num_samples):
            key = ','.join( [str(data.ix[n,parent]) for parent in P] )
            pdt = theta[node][key]
            data.ix[n,node] = draw(pdt)
    return data 
    
def impute_value(node, row, theta):
    # returns an imputed value for the given node in the given row
    cpt = theta[node]
    key = ','.join( [str(row[p]) for p in parents(node, adj)] )
    value = draw(cpt[key])
    return value

def impute_data(data, theta):
    # imputes a discrete value for every NaN in DataFrame data, 
    # and replaces the NaN with that imputed value
    for row_index in range(data.shape[0]):
        row = data.ix[row_index]
        nan_cols = row[row==NaN_Flag].index
        for node in nan_cols:
            data.ix[row_index, node] = impute_value(node, row, theta)

def impute_hidden_node(node, data, theta):

    num_rows = data.shape[0]
    
    C = children(node, adj) 
    print "children are ",
    print C
    
    # generate a table listing row indices for each combination of marginal variables
    marginal_indices = data.groupby(C).groups
    #print marginal_indices
    
    for r in xrange(num_rows):

        row = data.ix[r]
        
        likelihood_1 = 1.0
        for child in C:
            likelihood_1 *= theta[child]['1'][row[child]]  #TODO: this is really fragile..
        prior_1 = theta[node][''][1]
        
        likelihood_0 = 1.0
        for child in C:
            likelihood_0 *= theta[child]['0'][row[child]]  #TODO: this is really fragile..
        prior_0 = theta[node][''][0]
        
        child_vals = data.ix[r, C]
        marginal_likelihood = len(marginal_indices[tuple(data.ix[r,C])]) / float(num_rows)
        
        posterior_1 = likelihood_1 * prior_1 / marginal_likelihood
        posterior_0 = likelihood_0 * prior_0 / marginal_likelihood
        
        data.ix[r,node] = 1 if random.random() < posterior_1/(posterior_1+posterior_0) else 0    # HACK only works with binary variables
       
    #print "Sum of imputed probabilities was: %.2f" % sum_prob
    #print "Sum of imputed values was: %.2f" % data[node].sum()
        
def compute_theta(data):
    # if you have a complete set of data (no missing values), then
    # you can impute the CPTs by counting

    #print "sum of T in compute_theta is:"
    print data['T'].sum()
    
    result = {} 
    for col in data.columns:
        node = str(col)
        cpt = {}
        uniques = data[node].unique()  #TODO: compute this only once, globally
        P = parents(node, adj)
        #print P

        def simple_counts(series):
            ptable = {}
            total_count = float(len(series))
            for u in uniques:
                ptable[u] = sum(series==u) / total_count
            return ptable
        
        if P:
            groups = data.groupby(P).groups
            #print groups

            for key, indices in groups.iteritems():
                # for each unique combo of parent values...                     
                keystr = str(key) if len(P)<=1 else ','.join([str(v) for v in keytuple])
                cpt[keystr] = simple_counts(data.ix[indices, node])

        else:
            #print "no parents case"
            cpt[''] = simple_counts(data[node])
            
        #TODO:  handle the case where there are no examples of some keytuples?
        result[node] = cpt

    return result 

def log_likelihood(data, theta):
    # return the loglikelihood of an entire dataset according to theta
    # right now this is not used algorthmically.. just helpful to plot 
    # as a debugging diagnostic
    num_rows = data.shape[0]
    cols = data.columns
    pmap = parent_map(adj)

    log_likelihood = 0.0
    for r in xrange(num_rows):
        lhood = 1.0
        for col in cols:
            P = pmap[col]
            if P:
                lhood *= theta[col][str(int(data.ix[r,P]))][data.ix[r,col]]
            else:
                lhood *= theta[col][''][data.ix[r,col]]
            log_likelihood += math.log(lhood)
        
    print "Loglikelihood,%.4f" % log_likelihood
             

def learn(data, theta, max_iter):
    for i in range(max_iter):

        impute_hidden_node('T', data, theta)  # E-step
        theta = compute_theta(data)    # M-step

        print "Run %d produced theta of:" % i
        print_theta(theta) 
        #log_likelihood(data, theta)

#===============================================

#TODO: infer varaibles and state sizes from data
nodes = ['T', 'E1', 'E2', 'E3', 'E4']
N  = len(nodes)

# create a blank adjacency matrix, then 
# set the directed edges.  each row (node)  
# should have a 1 in the column of each parent.
adj = DataFrame.from_items( [(node, Series(np.zeros(N, int))) for node in nodes] )
adj.index = nodes
adj.ix['E1', 'T'] = 1
adj.ix['E2', 'T'] = 1
adj.ix['E3', 'T'] = 1
adj.ix['E4', 'T'] = 1
print adj

# specify the TRUE joint distribution, theta.  specified as a 
# dict of node -> cpt, where each cpt is a dict 
# of comma-separated values of the ordered parents -> prob
theta = {}
theta['T'] = {'': {0: 0.75, 1: 0.25}} 
theta['E1'] = {'0': {0: 0.45, 1: 0.55}, '1': {0: 0.05, 1: 0.95}, } 
theta['E2'] = {'0': {0: 0.40, 1: 0.60}, '1': {0: 0.05, 1: 0.95}, } 
theta['E3'] = {'0': {0: 0.50, 1: 0.50}, '1': {0: 0.10, 1: 0.90}, } 
theta['E4'] = {'0': {0: 0.60, 1: 0.40}, '1': {0: 0.25, 1: 0.75}, } 

# generate/simulate a dataset accoriding to theta 
row_count = 10000;  print "rowcount = %d" % row_count
df = simulate(adj, theta, row_count)
print df.mean() # just for debugging.. looks good
print df.corr() # just for debugging.. looks good

# hide the 'T' variable, to see if we can re-learn it
df2 = df.copy()
#df2['T'] = NaN_Flag 
df2['T'] =  (np.random.rand(row_count) > .6).astype(int)
theta_init = compute_theta(df2)

# try to learn back a new theta
print 'Goal:'
print_theta(theta)
print 'Starting Prior:'
print_theta(theta_init)

learn(data=df2, theta=theta_init, max_iter=300)
