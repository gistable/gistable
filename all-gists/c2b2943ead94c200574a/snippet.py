import caffe
import numpy as np
import os
import sys

# Author: Axel Angel, copyright 2015, license GPLv3.

class OwnContrastiveLossLayer(caffe.Layer):

    def setup(self, bottom, top):
        # check input pair
        if len(bottom) != 3:
            raise Exception("Need two inputs to compute distance.")

    def reshape(self, bottom, top):
        # check input dimensions match
        if bottom[0].count != bottom[1].count:
            raise Exception("Inputs must have the same dimension.")
        # difference is shape of inputs
        self.diff = np.zeros(bottom[0].num, dtype=np.float32)
        self.dist_sq = np.zeros(bottom[0].num, dtype=np.float32)
        self.zeros = np.zeros(bottom[0].num)
        self.m = 1.0
        # loss output is scalar
        top[0].reshape(1)

    def forward(self, bottom, top):
        GW1 = bottom[0].data
        GW2 = bottom[1].data
        Y = bottom[2].data
        loss = 0.0
        self.diff = GW1 - GW2
        self.dist_sq = np.sum(self.diff**2, axis=1)
        losses = Y * self.dist_sq \
           + (1-Y) * np.max([self.zeros, self.m - self.dist_sq], axis=0)
        loss = np.sum(losses)
        top[0].data[0] = loss / 2.0 / bottom[0].num

    def backward(self, top, propagate_down, bottom):
        Y = bottom[2].data
        disClose = np.where(self.m - self.dist_sq > 0.0, 1.0, 0.0)
        for i, sign in enumerate([ +1, -1 ]):
            if propagate_down[i]:
                alphas = np.where(Y > 0, +1.0, -1.0) * sign * top[0].diff[0] / bottom[i].num
                facts = ((1-Y) * disClose + Y) * alphas
                bottom[i].diff[...] = np.array([facts, facts]).T * self.diff
