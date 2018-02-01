""" 
Author: Oliver Mitevski

References:
A Generalized Linear Model for Principal Component Analysis of Binary Data, 
Andrew I. Schein; Lawrence K. Saul; Lyle H. Ungar

The code was translated and adapted from Jakob Verbeek's 
"Hidden Markov models and mixtures for Binary PCA" implementation in MATLAB

"""
import sys
from scipy import *
from numpy import *
from scipy.linalg import diagsvd, svd
from scipy.sparse import linalg
import cPickle, gzip, numpy, time
import pylab as p

from save_load import save_file, load_file


def	bpca(X, L=2, max_iters = 30):

		N, D = X.shape
		
		x = X
		X = 2*X - 1
		
		delta = random.permutation(N); Delta = X[delta[0],:]/100
		U = 1e-4*random.random( (N,L) )
		V = 1e-4*random.random( (L,D) )
		#for c=1:C; Th(:,:,c) = U(:,:,c)*V(:,:,c) + ones(N,1)*Delta(c,:); end;
		
		Th = zeros((N,D)); Th = dot( U, V) + outer(ones((N,1)),Delta)
		
		
		for iter in range(max_iters):
			print iter
			# Update U
			T= tanh(Th/2)/Th
			pp = outer(ones((N,1)),Delta[:])
			
			B = dot(V, (X - T*pp).T)
			
			for n in range(N):
				cc = outer(ones((L, 1)), T[n,:])
				A = dot(V*cc, V.T)
				U[n,:] = numpy.linalg.solve(A, B[:,n]).T
			
			Th = dot( U, V) + outer(ones((N,1)),Delta)
			
			
			Q = random.random(N) 
			#normalize it
			Q = sqrt(dot(Q,Q.conj()))
			
			# Update V
			T= tanh(Th/2)/Th
			U2 = c_[U, ones((N,1))]; 
			U2 = U2*tile(Q,(L+1,1)).T;
			B = dot(U2.T, X)
			
			for d in range(D):
				ff = outer(ones((L+1,1)),T[:,d].T)
				A = dot((U2.T * ff), c_[U, ones((N,1))])
				V2 = numpy.linalg.solve(A, B[:,d])
				Delta[d] = V2[-1]
				
				if L>0:
					V[:,d] = V2[0:-1]
					
			Th = dot( U, V) + outer(ones((N,1)),Delta)
	
		print U.shape
		
		#plotM1(U[0:10000:1,0:2], labels[0:10000:10])
		
		U1, S, V = svd(U); Vh = V.T
		U1, Vh = mat(U1[:,0:L]), mat(Vh[0:L,:]) 
		codes = array(U*Vh.T)
		
		return codes
		

def main():	
	# Load the dataset
	try:
		inputData = load_file(sys.argv[1])
		sparse = False
	except:
		print 'loading sparse'
		sparse = True
		from scipy.io import mmio as mm
		inputData = mm.mmread(sys.argv[1])
		inputData = array(inputData.todense())

	N, D = inputData.shape
	print N, D	
	
# make data binary
# 	for i in range(N):
#  		for j in range(D):
#  			if inputData[i,j] > 0.0:
#  				inputData[i,j] = 1.0
#  	save_file('news-10-stemmed.index2200/binDict', inputData)
# 	print 'saved binary'
	
	X = inputData

	labels = load_file(sys.argv[2])

	start = time.clock()

	codes = bpca(X, L=2, max_iters = 20)
	
	print "Time for computing binary PCA took", time.clock()-start
	
	save_file(sys.argv[3], codes)

	
if __name__ == "__main__":
	main()