#!/usr/bin/env python

"""
nsb_entropy.py

written by Sungho Hong, Computational Neuroscience Unit, Okinawa Institute of
Science and Technology

June, 2011

This script is a python version of Mathematica functions by Christian Mendl
implementing the Nemenman-Shafee-Bialek (NSB) estimator of entropy. For the
details of the method, check out the references below.

It depends on mpmath and numpy package.

References:
http://christian.mendl.net/pages/software.html
http://nsb-entropy.sourceforge.net
Ilya Nemenman, Fariel Shafee, and William Bialek. Entropy and Inference,
Revisited. arXiv:physics/0108025
Ilya Nemenman, William Bialek, and Rob de Ruyter van Steveninck. Entropy and
information in neural spike trains: Progress on the sampling problem. Physical
Review E 69, 056111 (2004)

"""
 
from mpmath import psi, rf, power, quadgl, mp, memoize
import numpy as np

DPS = 40

psi = memoize(psi)
rf = memoize(rf)
power = memoize(power)

def make_nxkx(n, K):
  """
  Return the histogram of the input histogram n assuming that the number of
  all bins is K.
  
  >>> from numpy import array
  >>> nTest = array([4, 2, 3, 0, 2, 4, 0, 0, 2])
  >>> make_nxkx(nTest, 9)
  {0: 3, 2: 3, 3: 1, 4: 2}
  """
  nxkx = {}
  nn = n[n>0]
  unn = np.unique(nn)
  for x in unn:
    nxkx[x] = (nn==x).sum()
  if K>nn.size:
    nxkx[0] = K-nn.size
  return nxkx

def _xi(beta, K):
  return psi(0, K*beta+1)-psi(0, beta+1)

def _dxi(beta, K):
  return K*psi(1, K*beta+1)-psi(1, beta+1)

def _S1i(x, nxkx, beta, N, kappa):
  return nxkx[x] * (x+beta)/(N+kappa) * (psi(0, x+beta+1)-psi(0, N+kappa+1))

def _S1(beta, nxkx, N, K):
  kappa = beta*K
  rx = np.array([_S1i(x, nxkx, beta, N, kappa) for x in nxkx])
  return -rx.sum()

def _rhoi(x, nxkx, beta):
  return power(rf(beta, np.double(x)), nxkx[x])

def _rho(beta, nxkx, N, K):  
  kappa = beta*K
  rx = np.array([_rhoi(x, nxkx, beta) for x in nxkx])
  return rx.prod()/rf(kappa, np.double(N))

def _Si(w, nxkx, N, K):
  sbeta = w/(1-w)
  beta = sbeta*sbeta
  return _rho(beta, nxkx, N, K) * _S1(beta, nxkx, N, K) * _dxi(beta, K) * 2*sbeta/(1-w)/(1-w)

def _measure(w, nxkx, N, K):
  sbeta = w/(1-w)
  beta = sbeta*sbeta
  return _rho(beta, nxkx, N, K) * _dxi(beta, K) * 2*sbeta/(1-w)/(1-w)

def S(nxkx, N, K):
  """
  Return the estimated entropy. nxkx is the histogram of the input histogram
  constructed by make_nxkx. N is the total number of samples, and K is the
  degree of freedom.
  
  >>> from numpy import array
  >>> nTest = array([4, 2, 3, 0, 2, 4, 0, 0, 2])
  >>> K = 9  # which is actually equal to nTest.size.
  >>> S(make_nxkx(nTest, K), nTest.sum(), K)
  1.940646728502697166844598206814653716492
  """
  mp.dps = DPS
  mp.pretty = True
  
  f = lambda w: _Si(w, nxkx, N, K)
  g = lambda w: _measure(w, nxkx, N, K)  
  return quadgl(f, [0, 1],maxdegree=20)/quadgl(g, [0, 1],maxdegree=20)

def _S2i_diag(x, nxkx, beta, N, kappa):
  xbeta = x+beta
  Nkappa2 = N+kappa+2
  psNK2 = psi(0, Nkappa2)
  ps1NK2 = psi(1, Nkappa2)
  
  s1  = (psi(0, xbeta+2)-psNK2)**2 + psi(1, xbeta+2) - ps1NK2
  s1 *= nxkx[x]*xbeta*(xbeta+1)
  
  s2 = (psi(0, xbeta+1)-psNK2)**2 - ps1NK2
  s2 *= nxkx[x]*(nxkx[x]-1)*xbeta*xbeta
  
  return s1+s2

def _S2i_nondiag(x1, x2, nxkx, beta, N, kappa):
  psNK2 = psi(0, N+kappa+2)
  ps1NK2 = psi(1, N+kappa+2)
  x1beta = x1+beta
  x2beta = x2+beta
  
  s1 = (psi(0, x1beta+1)-psNK2)*(psi(0, x2beta+1)-psNK2) - ps1NK2
  s1 = s1*nxkx[x1]*nxkx[x2]*x1beta*x2beta

  return s1

def _S2(beta, nxkx, N, K):
  kappa = beta*K
  Nkappa = N+kappa
  nx = np.array(nxkx.keys())
  Nnx = nx.size
  
  dsum = 0.0
  for x in nx:
    dsum = dsum + _S2i_diag(x, nxkx, beta, N, kappa)
  
  ndsum = 0.0
  for i in xrange(Nnx-1):
    x1 = nx[i]
    for j in xrange(i+1, Nnx):
      x2 = nx[j]
      if x1==x2:
        ndsum = ndsum + _S2i_diag(x1, nxkx, beta, N, kappa)
      else:
        ndsum = ndsum + _S2i_nondiag(x1, x2, nxkx, beta, N, kappa)
  return (dsum + 2*ndsum)/(Nkappa)/(Nkappa+1)

def _dSi(w, nxkx, N, K):
  sbeta = w/(1-w)
  beta = sbeta*sbeta
  return _rho(beta, nxkx, N, K) * _S2(beta, nxkx, N, K) * _dxi(beta, K) * 2*sbeta/(1-w)/(1-w)

def dS(nxkx, N, K):
  """
  Return the mean squared flucuation of the entropy.
  
  >>> from numpy import array, sqrt
  >>> nTest = np.array([4, 2, 3, 0, 2, 4, 0, 0, 2])
  >>> K = 9  # which is actually equal to nTest.size.
  >>> nxkx = make_nxkx(nTest, K)
  >>> s = S(nxkx, nTest.sum(), K)
  >>> ds = dS(nxkx, nTest.sum(), K)
  >>> ds
  3.790453283682443237187782792251041316212
  >>> sqrt(ds-s**2) # the standard deviation for the estimated entropy.
  0.1560242251518078487118059349690693094484
  """  
  
  mp.dps = DPS
  mp.pretty = True
  
  f = lambda w: _dSi(w, nxkx, N, K)
  g = lambda w: _measure(w, nxkx, N, K)  
  return quadgl(f, [0, 1],maxdegree=20)/quadgl(g, [0, 1],maxdegree=20)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
