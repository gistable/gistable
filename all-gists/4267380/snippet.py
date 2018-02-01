#Forward-backward algorithm implementation in Theano, 
#with example taken from Wikipedia: 
#http://en.wikipedia.org/wiki/Forward%E2%80%93backward_algorithm

import theano
import theano.tensor as T
import numpy as np

#Set up vectors, etc to represent 
#observations, indexes into the observation
#vector and the distribution of outcomes
obs_vec = T.ivector('obs_vec')
obs_type = T.iscalar('obs_type')
emission_tensor = T.dmatrix('emission')

#Expression for extracting the right row out of the emission matrix 
extract_e = emission_tensor[obs_type] * T.eye(T.shape(emission_tensor)[1], m = T.shape(emission_tensor)[1])

#Transition matrix
tmat_tensor = T.dmatrix('tmat')

#Backward probability of the final observation, given the 
#evidence, so just a vector of ones
final_probs_tensor = T.dvector('final_probs')

#Holds the prior probabilities of system states @ t = 0
init_probs_tensor = T.dvector('init_probs')

#Expression for calculating one step of the forward probabilities
f_ex = (T.dot(T.dot(init_probs_tensor, tmat_tensor), extract_e)).T
f_fn = theano.function([init_probs_tensor, tmat_tensor, emission_tensor, obs_type], f_ex)

#Expression for calculating one step of the backward probabilities
b_ex = (T.dot(tmat_tensor, T.dot(final_probs_tensor, extract_e)))
b_fn = theano.function([tmat_tensor, final_probs_tensor, emission_tensor, obs_type], b_ex)

#Set up to do the entire forward sweep
def forwardIteration(st, ip, tmat, em):
  e_e = em[st] * T.eye(T.shape(em)[1], m = T.shape(em)[1])
	z = (T.dot(T.dot(ip, tmat), e_e)).T
	return z / T.sum(z)
	
result, updates = theano.scan(fn = forwardIteration, outputs_info = init_probs_tensor, non_sequences = [tmat_tensor, emission_tensor], sequences = obs_vec, n_steps = obs_vec.shape[0])

f_r = T.concatenate((init_probs_tensor.dimshuffle('x',0), result))
f_fn = theano.function(inputs = [init_probs_tensor, tmat_tensor, emission_tensor, obs_vec], outputs = f_r)

#Entire backward sweep
def backwardIteration(st, lp, tmat, em):	
	e_e = em[st] * T.eye(T.shape(em)[1], m = T.shape(em)[1])
	z = (T.dot(tmat, T.dot(lp, e_e)))
	return z / T.sum(z)

b_result, b_updates = theano.scan(fn = backwardIteration, outputs_info = final_probs_tensor, non_sequences = [tmat_tensor, emission_tensor], sequences = obs_vec, n_steps = obs_vec.shape[0], go_backwards = True)

#Be sure to put the final probabilities at the beginning of the (reversed)
#backward probabilities
b_r = T.concatenate((final_probs_tensor.dimshuffle('x',0), b_result))
b_fn = theano.function(inputs = [final_probs_tensor, tmat_tensor, emission_tensor, obs_vec], outputs = b_r)

#Now define a scan that computes the smoothed probabilities

#To reverse the backward probabilities, we provide an index and the length
#of dimension 1 of the backward prob matrix. 

#Is there a better way of reversing a sequence while iterating over 
#another forwards w/o an additional call to scan to reverse the original?
def smoothingIteration(f_val, f_index, b_vals, max_index):
	x = b_vals[max_index - f_index-1]
	s = f_val*x
	return s / T.sum(s)

s_result, s_updates = theano.scan(fn = smoothingIteration, outputs_info = None, non_sequences = [b_r,  b_r.shape[0]], sequences = [f_r, T.arange(10000)])

s_fn = theano.function(inputs = [init_probs_tensor, final_probs_tensor, tmat_tensor, emission_tensor, obs_vec], outputs = s_result)

#This function is supposed to obtain the smoothed state probabilities
#from a vector passed as obs_series, given the initial probs, final
#probs and emission matrix
def smoothedSeries(obs_series, init_probs, final_probs, tmat, emission):	
	f_result, updates = theano.scan(fn = forwardIteration, outputs_info = init_probs, non_sequences = [tmat, emission], sequences = obs_series, n_steps = obs_series.shape[0])

	f_r = T.concatenate((init_probs.dimshuffle('x',0), f_result))

	b_result, b_updates = theano.scan(fn = backwardIteration, outputs_info = final_probs, non_sequences = [tmat, emission], sequences = obs_series, n_steps = obs_series.shape[0], go_backwards = True)

	b_r = T.concatenate((final_probs.dimshuffle('x',0), b_result))

	s_result, s_updates = theano.scan(fn = smoothingIteration, outputs_info = None, non_sequences = [b_r,  b_r.shape[0]], sequences = [f_r, T.arange(10000)])

	return s_result

#Integer matrix with rows holding independent observation series
obs_mat = T.imatrix('obs_matrix')

all_result, all_updates = theano.map(fn = smoothedSeries, non_sequences = [init_probs_tensor, final_probs_tensor, tmat_tensor, emission_tensor], sequences = obs_mat)

all_fn = theano.function(inputs = [obs_mat, init_probs_tensor, final_probs_tensor, tmat_tensor, emission_tensor], outputs = all_result)


if __name__ == '__main__':

	#Flat prior over initial states
	initProbs = np.array([0.5, 0.5])

	#Probability of final observation given 
	#future unobserved state, i.e. 1.0
	lastProb = np.array([1.0, 1.0])
	
	#Transition matrix
	tmat = np.array([[0.7, 0.3], [0.3, 0.7]])

	#Single observation vector
	obs = np.array([0, 0, 1, 0, 0, 1, 1, 1], dtype = np.int32)

	#Observation matrix
	obsb = np.array([[0, 0, 1, 0, 0, 1, 1, 1] for i in xrange(10)], dtype = np.int32)

	#Categorical emission distribution
	emission = np.array([[0.9, 0.1], [0.2, 0.8]])
	emission = emission.T

	#Calculate forward probabilities
	print("Forward probs:")
	o = f_fn(initProbs, tmat, emission, obs)
	print(o)

	#Calculate backward probabilities
	print("Backward probs:")
	o2 = b_fn(lastProb, tmat, emission, obs)
	print(o2)

	#Calculate smoothed probabilities
	o3 = s_fn(initProbs, lastProb, tmat, emission, obs)
	print("Smoothed probs:")
	print(o3)

	#Try to compute smoothed probabilities for each 
	#row of a matrix of observations, with same prior
	#transmission matrix and emission probabilities
	o4 = all_fn(obsb, initProbs, lastProb, tmat, emission)
	print("Smoothed probs in bulk:")
	print(o4)
