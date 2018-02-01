
# coding: utf-8
 
"""Online learning."""

import numpy as np
from numpy import sign
import itertools as it
from numpy import array as A, zeros as Z
import math
import pickle
import time
import random 
import collections, os
        


def poly(degree):
    def kernel(a,b):
        norm = np.sqrt(np.dot(a,a)*np.dot(b,b))
        if norm == 0.: return 0.
        return ((1+np.dot(a,b)/norm)**degree)
    return kernel

def rbf(var):
    def kernel(a,b):
        d = a-b
        return math.exp(-var*np.dot(d,d))
    return kernel



class LaSVM(object):
    def __init__(self, C, kernel, tau, eps=0.001):
        self.S = []
        self.a = []
        self.g = []
        self.y = []
        self.C = C
        self.k = kernel
        self.tau = tau
        self.eps = eps
        self.b = 0
        self.delta = 0
        self.i = 0
        self.misses = 0
        
    def predict(self, v):
        return sum(self.a[i]*self.k(self.S[i],v) for i in xrange(len(self.S)))

    def A(self, i):
        return min(0, self.C*self.y[i])
    
    def B(self, i):
        return max(0, self.C*self.y[i])

    def tau_violating(self, i, j):
        return ((self.a[i] < self.B(i)) and
                (self.a[j] > self.A(j)) and
                (self.g[i] - self.g[j] > self.tau))

    def extreme_ij(self):
        S = self.S
        i = np.argmax(list((self.g[i] if self.a[i]<self.B(i) else -np.inf)
                           for i in xrange(len(S))))
        j = np.argmin(list((self.g[i] if self.a[i]>self.A(i) else np.inf)
                           for i in xrange(len(S))))
        return i,j

    def lbda(self, i, j):
        S = self.S
        l= min((self.g[i]-self.g[j])/(self.k(S[i],S[i])+self.k(S[j],S[j])-self.k(S[i],S[j])),
               self.B(i)-self.a[i],
               self.a[j]-self.A(j))
        self.a[i] += l
        self.a[j] -= l
        for s in xrange(len(S)):
            self.g[s] -= l*(self.k(S[i],S[s])-self.k(S[j],S[s]))
        return l

    
    def lasvm_process(self, v, cls, w):
        self.S.append(v)
        self.a.append(0)
        self.y.append(cls)
        self.g.append(cls - self.predict(v))
        if cls > 0:
            i = len(self.S)-1
            foo, j = self.extreme_ij()
        else:
            j = len(self.S)-1
            i, foo = self.extreme_ij()
        if not self.tau_violating(i, j): return
        S = self.S
        lbda = self.lbda(i,j)

    def lasvm_reprocess(self):
        S = self.S
        i,j = self.extreme_ij()
        if not self.tau_violating(i,j): return
        lbda = self.lbda(i,j)
        i,j = self.extreme_ij()
        to_remove = []
        for s in xrange(len(S)):
            if self.a[s] < self.eps:
                to_remove.append(s)
        for s in reversed(to_remove):
            del S[s]
            del self.a[s]
            del self.y[s]
            del self.g[s]
        i,j = self.extreme_ij()
        self.b = (self.g[i]+self.g[j])/2.
        self.delta = self.g[i]-self.g[j]

    def update(self, v, c, w):
        if len(self.S) < 10:
            self.S.append(v)
            self.y.append(c)
            self.a.append(c)
            self.g.append(0)
            for i in xrange(len(self.S))
                self.g[i] = self.y[i]-self.predict(self.S[i])
        else:
            if c*(self.predict(v) + self.b) < 0:
                self.misses += 1
            self.i += 1
            self.lasvm_process(v,c,w)
            self.lasvm_reprocess()
            self.lasvm_reprocess()
            if self.i % 1000 == 0:
                print "m", self.misses, "s", len(self.S)
                self.misses = 0
