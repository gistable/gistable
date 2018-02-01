# -*- coding: utf-8 -*-

# Copyright (C) 2010 Mathieu Blondel
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Implementation details are described at
# http://www.mblondel.org/journal/2010/06/21/semi-supervised-naive-bayes-in-python/

import numpy as np

"""
Implementation of Naive Bayes trained by EM for semi-supervised text
classification, as described in

"Semi-Supervised Text Classification Using EM", by Nigam et al.

Notation:

    w: word
    d: document
    c: class

    V: vocabulary size
    X: number of documents
    M: number of classes
"""

def softmax(loga, k=-np.inf, out=None):
    """
    Compute the sotfmax function (normalized exponentials) without underflow.

    exp^a_i / \sum_j exp^a_j
    """
    if out is None: out = np.empty_like(loga).astype(np.double)
    m = np.max(loga)
    logam = loga - m
    sup = logam > k
    inf = np.logical_not(sup)
    out[sup] = np.exp(logam[sup])
    out[inf] = 0.0
    out /= np.sum(out)
    return out

def logsum(loga, k=-np.inf):
    """
    Compute a sum of logs without underflow.

    \log \sum_c e^{b_c} = log [(\sum_c e^{b_c}) e^{-B}e^B]
                        = log [(\sum_c e^{b_c-B}) e^B]
                        = [log(\sum_c e^{b_c-B}) + B

    where B = max_c b_c
    """
    B = np.max(loga)
    logaB = aB = loga - B
    sup = logaB > k
    inf = np.logical_not(sup)
    aB[sup] = np.exp(logaB[sup])
    aB[inf] = 0.0
    return (np.log(np.sum(aB)) + B)

def loglikelihood(td, delta, tdu, p_w_c_log, p_c_log):
    V, Xl = td.shape
    V_, Xu = tdu.shape
    Xl_, M = delta.shape

    lik = 0.0

    ## labeled
    # log P(x|c)
    p_x_c_log = np.zeros((Xl,M), np.double)
    for w,d in zip(*td.nonzero()):
        p_x_c_log[d,:] += p_w_c_log[w,:] * td[w,d]

    # add log P(c) + lop P(x|c) if x has label c
    for d,c in zip(*delta.nonzero()):
        lik += p_c_log[c] + p_x_c_log[d,c]

    ## unlabelled
    # log P(x|c)
    p_x_c_log = np.zeros((Xu,M), np.double)
    for w,d in zip(*tdu.nonzero()):
        p_x_c_log[d,:] += p_w_c_log[w,:] * tdu[w,d]

    # add log P(c)
    p_x_c_log += p_c_log[np.newaxis,:]

    for d in range(Xu):
        lik += logsum(p_x_c_log[d,:], k=-10)

    return lik

def normalize_p_c(p_c):
    M = len(p_c)
    denom = M + np.sum(p_c)
    p_c += 1.0
    p_c /= denom

def normalize_p_w_c(p_w_c):
    V, X = p_w_c.shape
    denoms = V + np.sum(p_w_c, axis=0)
    p_w_c += 1.0
    p_w_c /= denoms[np.newaxis,:]

class SemiNB(object):

    def __init__(self, model=None):
        """
        model: a model, as returned by get_model() or train().
        """
        self.p_w_c = None
        self.p_c = None
        if model is not None: self.set_model(model)
        self.debug = False

    def train(self, td, delta, normalize=True, sparse=True):
        """
        td: term-document matrix V x X
        delta: X x M matrix
               where delta(d,c) = 1 if document d belongs to class c
        """

        X_, M = delta.shape
        V, X = td.shape
        assert(X_ == X)

        # P(c)
        self.p_c = np.sum(delta, axis=0)

        # P(w|c)
        self.p_w_c = np.zeros((V,M), dtype=np.double)

        if sparse:
            # faster when delta is sparse
            # select indices of documents that have class c
            for d,c in zip(*delta.nonzero()):
                # select indices of terms that are non-zero
                for w in np.flatnonzero(td[:,d]):
                    self.p_w_c[w,c] += td[w,d] * delta[d,c]
        else:
            # faster when delta is non-sparse
            for w,d in zip(*td.nonzero()):
                self.p_w_c[w,:] += td[w,d] * delta[d,:]

        if normalize:
            normalize_p_c(self.p_c)
            normalize_p_w_c(self.p_w_c)

        return self.get_model()

    def train_semi(self, td, delta, tdu, maxiter=50, eps=0.01):
        """
        td: V x X term document matrix
        delta: X x M label matrix
        tdu: V x Xu term document matrix (unlabeled)
        maxiter: maximum number of iterations
        eps: stop if no more progress than esp
        """
        X_, M = delta.shape
        V, X = td.shape
        assert(X_ == X)

        # compute counts for labeled data once for all
        self.train(td, delta, normalize=False)
        p_c_l = np.array(self.p_c, copy=True)
        p_w_c_l = np.array(self.p_w_c, copy=True)

        # normalize to get initial classifier
        normalize_p_c(self.p_c)
        normalize_p_w_c(self.p_w_c)

        lik = loglikelihood(td, delta, tdu, np.log(self.p_w_c), np.log(self.p_c))

        for iteration in range(1, maxiter+1):
            # E-step: find the probabilistic labels for unlabeled data
            delta_u = self.predict_proba_all(tdu)

            # M-step: train classifier with the union of
            #         labeled and unlabeled data
            self.train(tdu, delta_u, normalize=False, sparse=False)
            self.p_c += p_c_l
            self.p_w_c += p_w_c_l
            normalize_p_c(self.p_c)
            normalize_p_w_c(self.p_w_c)

            lik_new = loglikelihood(td, delta, tdu,
                                    np.log(self.p_w_c), np.log(self.p_c))
            lik_diff = lik_new - lik
            assert(lik_diff >= -1e-10)
            lik = lik_new

            if lik_diff < eps:
                print "No more progress, stopping EM at iteration", iteration
                break

            if self.debug:
                print "Iteration", iteration
                print "L += %f" % lik_diff

        return self.get_model()

    def p_x_c_log_all(self, td):
        M = len(self.p_c)
        V, X = td.shape
        p_x_c_log = np.zeros((X,M), np.double)
        p_w_c_log = np.log(self.p_w_c)

        # log P(x|c)
        for w,d in zip(*td.nonzero()):
            p_x_c_log[d,:] += p_w_c_log[w,:] * td[w,d]

        return p_x_c_log

    def predict_proba(self, x):
        """
        x: a V array representing a document

        Compute a M array containing P(c|x).
        """
        return self.predict_proba_all(x[:,np.newaxis])[0,:]

    def predict_proba_all(self, td):
        """
        td: V x X term document matrix

        Compute an X x M matrix of P(c|x) for all x in td.
        """
        V, X = td.shape

        # log P(x|c)
        p_x_c_log = self.p_x_c_log_all(td)

        # add log P(c)
        p_x_c_log += np.log(self.p_c)[np.newaxis,:]

        # sotfmax(log P(x|c) + log P(c)) = P(c|x)
        for d in range(X):
            softmax(p_x_c_log[d,:], k=-10, out=p_x_c_log[d,:])

        return p_x_c_log

    def predict(self, x):
        """
        x: a V array representing a document

        Compute the predicted class index.
        """
        return self.predict_all(x[:,np.newaxis])[0]

    def predict_all(self, td):
        """
        td: V x X term document matrix

        Compute a X array containing predicted class indices.

        Note: the main difference with predict_proba_all is that the
              normalization is not necessary, as we are only interested in the most
              likely class.
        """

        # log P(x|c)
        p_x_c_log = self.p_x_c_log_all(td)

        # add log P(c)
        p_x_c_log += np.log(self.p_c)[np.newaxis,:]

        return p_x_c_log.argmax(axis=1)

    def get_model(self):
        return (self.p_w_c, self.p_c)

    def set_model(self, model):
        self.p_w_c, self.p_c = model

