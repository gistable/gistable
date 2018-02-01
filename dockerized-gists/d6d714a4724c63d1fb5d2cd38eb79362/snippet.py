#!/usr/bin/env python2
# Implementation of visual encryption generator from
# http://www.datagenetics.com/blog/november32013/index.html
#
# The input files are three png images and should be placed in the same directory.
# The names are hardcoded:
# in1.png, in2.png : input images that are used on the encoded images
# hidden.png : input image that is shown when encoded images are overlayed

import numpy as np
import matplotlib.image as mpimg
import random

# When a pixel is considered black
GRAY_CUTOFF = 0.5
# Enlargement factor for output encoded images
ENLARGE_FACTOR = 5

RGB_WHITE = np.array([1, 1, 1, 0])
RGB_BLACK = np.array([0, 0, 0, 1])

def loadImage(filename):

    return mpimg.imread(filename)

def saveImage(imageArray, filename):

    mpimg.imsave(filename, imageArray)

def encode(in1, in2, hidden):

    # Sizes of all inputs should match, we don't care about the alpha
    if not (in1.shape[0] == in2.shape[0] == hidden.shape[0] and
            in1.shape[1] == in2.shape[1] == hidden.shape[1]):
        raise RuntimeError("Shapes of the images do not match")
    (xsize, ysize) = (in1.shape[0], in1.shape[1])

    outshape = (2*xsize*ENLARGE_FACTOR, 2*ysize*ENLARGE_FACTOR, len(RGB_WHITE))
    out1 = np.empty(outshape)
    out2 = np.empty(outshape)

    def getBW(i, j, array):
        norm = np.linalg.norm(array[i,j][1:3])
        return norm < GRAY_CUTOFF

    def setElements(i, j, enc):
        def setElemArray(x, y, enc, arr):
            for i in xrange(2):
                for j in xrange(2):
                    for e_i1 in xrange(ENLARGE_FACTOR):
                        for e_i2 in xrange(ENLARGE_FACTOR):
                            arr[x*2*ENLARGE_FACTOR+i*ENLARGE_FACTOR+e_i1,y*2*ENLARGE_FACTOR+j*ENLARGE_FACTOR+e_i2] = RGB_BLACK if enc[i,j] else RGB_WHITE

        setElemArray(i, j, enc[0], out1)
        setElemArray(i, j, enc[1], out2)

    def generateEncoding(h, i1, i2):
        blockSize = (2, 2)
        def generateRandomPixels(N):
            if N > 4:
                raise Exception("Programming error: generateRandomPixels should be called with N < 4!")
            availablePositions = range(4)
            out = []
            for i in range(N):
                rnd = random.choice(availablePositions)
                availablePositions.remove(rnd)
                out.append(rnd)
            return out

        def BBB():
            [rnd1, rnd2] = generateRandomPixels(2)
            (e1, e2) = (np.ones(4), np.ones(4))
            e1[rnd1] = e2[rnd2] = 0
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
        
        def BBW():
            [rnd1, rnd2, rnd3] = generateRandomPixels(3)
            (e1, e2) = (np.ones(4), np.ones(4))
            e1[rnd1] = e2[rnd2] = e2[rnd3] = 0
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
        
        def BWB():
            (e1, e2) = BBW()
            return (e2, e1)
            
        def BWW():
            [rnd1, rnd2] = generateRandomPixels(2)
            e1 = np.ones(4)
            e1[rnd1] = e1[rnd2] = 0
            e2 = np.ones(4) - e1
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
        
        def WBB():
            [rnd] = generateRandomPixels(1)
            (e1, e2) = (np.ones(4), np.ones(4))
            e1[rnd] = e2[rnd] = 0
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
        
        def WBW():
            [rnd1, rnd2] = generateRandomPixels(2)
            (e1, e2) = (np.ones(4), np.ones(4))
            e1[rnd1] = e2[rnd1] = e2[rnd2] = 0
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
        
        def WWB():
            (e1, e2) = WBW()
            return (e2, e1)

        def WWW():
            [rnd1, rnd2, rnd3] = generateRandomPixels(3)
            (e1, e2) = (np.ones(4), np.ones(4))
            e1[rnd1] = e2[rnd1] = e1[rnd2] = e2[rnd3] = 0
            return (np.reshape(e1, blockSize), np.reshape(e2, blockSize))
            
        if h:
            if i1:
                if i2:
                    return BBB()
                else:
                    return BBW()
            else:
                if i2:
                    return BWB()
                else:
                    return BWW()
        else:
            if i1:
                if i2:
                    return WBB()
                else:
                    return WBW()
            else:
                if i2:
                    return WWB()
                else:
                    return WWW()
            

    for i in xrange(xsize):
        for j in xrange(ysize):
            enc = generateEncoding(getBW(i,j,hidden), getBW(i,j,in1), getBW(i,j,in2))
            setElements(i, j, enc)

    return (out1, out2)

if __name__ == "__main__":
    hidden = loadImage("hidden.png")
    in1 = loadImage("in1.png")
    in2 = loadImage("in2.png")

    (out1, out2) = encode(in1, in2, hidden)

    saveImage(out1, "out1.png")
    saveImage(out2, "out2.png")
