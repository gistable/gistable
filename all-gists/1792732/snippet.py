#!/usr/bin/python
"""
Author: Jeremy M. Stober
Program: TILES.PY
Date: Monday, March 31 2008
Description: A simple CMAC implementation.
"""

import os, sys, getopt, pdb
from numpy import *
from numpy.random import *
import pylab
from  mpl_toolkits.mplot3d import Axes3D
import pickle

pylab.ioff()


class CMAC(object):

    def __init__(self, nlevels, quantization, beta):
        self.nlevels = nlevels
        self.quantization = quantization
        self.weights = {}
        self.beta = beta

    def save(self,filename):
        pickle.dump(self,open(filename,'wb'),pickle.HIGHEST_PROTOCAL)

    def quantize(self, vector):
        """
        Generate receptive field coordinates for each level of the CMAC.
        """

        quantized = (vector / self.quantization).astype(int)
        coords = []

        for i in range(self.nlevels):
            # Note that the tile size is nlevels * quantization!

            # Coordinates for this tile.
            point = list(quantized - (quantized - i) % self.nlevels)

            # Label the ith tile so that it gets hashed uniquely.
            point.append(i)

            coords.append(tuple(point))

        return coords

    def difference(self, vector, delta, quantized = False):
        """
        Train the CMAC using the difference instead of the response.
        """

        # Coordinates for each level tiling.
        coords = None
        if quantized == False:
            coords = self.quantize(vector)
        else:
            coords = vector

        error = self.beta * delta # delta = response - prediction

        for pt in coords:
            self.weights[pt] += error

        return delta


    def response(self, vector, response, quantized = False):
        """
        Train the CMAC.
        """

        # Coordinates for each level tiling.
        coords = None
        if quantized == False:
            coords = self.quantize(vector)
        else:
            coords = vector

        # Use Python's own hashing for storing feature weights. If you
        # roll your own you'll have to learn about Universal Hashing.
        prediction = sum([self.weights.setdefault(pt, 0.0) for pt in coords]) / len(coords)
        error = self.beta * (response - prediction)

        for pt in coords:
            self.weights[pt] += error

        return prediction

    def __len__(self):
        return len(self.weights)

    def eval(self, vector, quantized = False):
        """
        Eval the CMAC.
        """

        # Coordinates for each level tiling.
        coords = None
        if quantized == False:
            coords = self.quantize(vector)
        else:
            coords = vector

        return sum([self.weights.setdefault(pt, 0.0) for pt in coords]) / len(coords)

def test(name):

    if name == 'sin':

        cmac = CMAC(32, .01, 0.1)
        points = uniform(low=0,high=2*pi,size=1000)
        responses = sin(points)

        errors = []
        for (point,response) in zip(points,response):
            predicted = cmac.response(array([point]),response)
            errors.append(abs(response - predicted))
            #print point, response, predicted

        points = uniform(low=0, high=2*pi, size=100)
        actual = []
        for point in points:
            actual.append(cmac.eval(array([point])))

        pylab.figure(1)
        pylab.plot(points,actual, '.')

        pylab.figure(2)
        pylab.plot(errors)

        pylab.show()

    elif name == 'wave':

        cmac = CMAC(32, .1, 0.01)
        points = uniform(low=0,high=2*pi,size=(10000,2))
        responses = sin(points[:,0]) + cos(points[:,1])

        errors = []
        for (point,response) in zip(points,responses):
            predicted = cmac.response(point,response)
            errors.append(abs(response - predicted))
            #print point, response, predicted


        fig1 = pylab.figure(1)
        #ax1 = fig1.add_subplot(111,projection='3d')
        ax1 = Axes3D(fig1)
        ax1.scatter(points[:,0], points[:,1], responses)

        points = uniform(low=0,high=2*pi,size=(10000,2))
        predictions = []
        for point in points:
            predictions.append(cmac.eval(point))

        fig2 = pylab.figure(2)
        #ax2 = fig2.add_subplot(111,projection='3d')
        ax2 = Axes3D(fig2)
        ax2.scatter(points[:,0], points[:,1], predictions)

        # print len(cmac)
        # pylab.plot(errors)
        pylab.show()


def main():

    def usage():
	print sys.argv[0] + "[-h] [-d]"

    try:
        (options, args) = getopt.getopt(sys.argv[1:], 'dh', ['help','debug'])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    for o, a in options:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
	elif o in ('-d', '--debug'):
	    pdb.set_trace()

    test('wave')

if __name__ == "__main__":
    main()
