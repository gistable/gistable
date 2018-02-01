#! encoding=UTF-8
"""
kernel canonical correlation analysis
"""

import numpy as np
from scipy.linalg import svd
from sklearn.metrics.pairwise import pairwise_kernels, euclidean_distances

class KCCA(object):
	def __init__(self, n_components=1, epsilon=1.0, kernel="linear", degree=3, gamma=None, coef0=1, n_jobs=1):
		self.n_components = n_components
		self.epsilon = epsilon
		self.kernel = kernel
		self.degree = degree
		self.gamma = gamma
		self.coef0 = coef0
		self.n_jobs = n_jobs

	def fit(self, X, Y):
		ndata_x, nfeature_x = X.shape
		ndata_y, nfeature_y = Y.shape
		if ndata_x != ndata_y:
			raise Exception("Inequality of number of data between X and Y")

		if self.kernel != "precomputed":
			Kx = self._pairwise_kernels(X)
			Ky = self._pairwise_kernels(Y)

		I = self.epsilon * np.identity(ndata_x)
		KxI_inv = np.linalg.inv(Kx + I)
		KyI_inv = np.linalg.inv(Ky + I)
		L = np.dot(KxI_inv, np.dot(Kx, np.dot(Ky, KyI_inv)))
		U, s, Vh = svd(L)

		self.alpha = np.dot(KxI_inv, U[:, :self.n_components])
		self.beta = np.dot(KyI_inv, Vh.T[:, :self.n_components])
		return self

	def _pairwise_kernels(self, X, Y=None):
		return pairwise_kernels(X, Y, metric=self.kernel, filter_params=True, n_jobs=self.n_jobs, degree=self.degree, gamma=self.gamma, coef0=self.coef0)


if __name__ == "__main__":
	X = np.random.normal(size=(1000,100))
	Y = np.random.normal(size=(1000,20))
	kcca = KCCA(n_components=10, kernel="rbf", n_jobs=1, epsilon=0.1).fit(X, Y)

	"""
	matching on test data
	"""
	alpha = kcca.alpha
	beta = kcca.beta
	X_te = np.random.normal(size=(10,100))
	Y_te = np.random.normal(size=(10,20))
	Kx = kcca._pairwise_kernels(X_te, X)
	Ky = kcca._pairwise_kernels(Y_te, Y)
	F = np.dot(Kx, alpha)
	G = np.dot(Ky, beta)
	D = euclidean_distances(F, G)
	idx_pred = np.argmin(D, axis=0)
	print "matching result:", idx_pred

	"""
	similarity between true object and predicted object on test data
	"""
	idx_true = range(10)
	C = pairwise_kernels(Y_te[idx_true], Y_te[idx_pred], metric="cosine")
	print "1-best mean similarity:", np.mean(C.diagonal())



