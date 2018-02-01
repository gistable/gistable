#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright INRIA
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
#
# DANA is a computing framework for the simulation of distributed,
# asynchronous, numerical and adaptive models.
#
# This software is governed by the CeCILL license under French law and abiding
# by the rules of distribution of free software. You can use, modify and/ or
# redistribute the software under the terms of the CeCILL license as circulated
# by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info/index.en.html.
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean that
# it is complicated to manipulate, and that also therefore means that it is
# reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# -----------------------------------------------------------------------------
'''
Reaction Diffusion : Gray-Scott model

References:
----------
Complex Patterns in a Simple System
John E. Pearson, Science 261, 5118, 189-192, 1993.
'''
from sys import stderr
from itertools import product

import numpy as np
import scipy.sparse as sp



def convolution_matrix(src, dst, kernel, toric=True):
    '''
    Build a sparse convolution matrix M such that:

    (M*src.ravel()).reshape(src.shape) = convolve2d(src,kernel)

    You can specify whether convolution is toric or not and specify a different
    output shape. If output (dst) is different, convolution is only applied at
    corresponding normalized location within the src array.

    Building the matrix can be pretty long if your kernel is big but it can
    nonetheless saves you some time if you need to apply several convolution
    compared to fft convolution (no need to go to the Fourier domain).

    Parameters:
    -----------

    src : n-dimensional numpy array
        Source shape

    dst : n-dimensional numpy array
        Destination shape

    kernel : n-dimensional numpy array
        Kernel to be used for convolution

    Returns:
    --------

    A sparse convolution matrix

    Examples:
    ---------

    >>> Z = np.ones((3,3))
    >>> M = convolution_matrix(Z,Z,Z,True)
    >>> print (M*Z.ravel()).reshape(Z.shape)
    [[ 9.  9.  9.]
     [ 9.  9.  9.]
     [ 9.  9.  9.]]
    >>> M = convolution_matrix(Z,Z,Z,False)
    >>> print (M*Z.ravel()).reshape(Z.shape)
    [[ 4.  6.  4.]
     [ 6.  9.  6.]
     [ 4.  6.  4.]]
    '''

    # Get non NaN value from kernel and their indices.
    nz = (1 - np.isnan(kernel)).nonzero()
    data = kernel[nz].ravel()
    indices = [0,]*(len(kernel.shape)+1)
    indices[0] = np.array(nz)
    indices[0] += np.atleast_2d((np.array(src.shape)//2 - np.array(kernel.shape)//2)).T

    # Generate an array A for a given shape such that given an index tuple I,
    # we can translate into a flat index F = (I*A).sum()
    to_flat_index = np.ones((len(src.shape),1), dtype=int)
    if len(src.shape) > 1:
        to_flat_index[:-1] = src.shape[1]

    R, C, D = [], [], []
    dst_index = 0
    src_indices = []

    # Translate target tuple indices into source tuple indices taking care of
    # possible scaling (this is done by normalizing indices)
    for i in range(len(src.shape)):
        z = np.rint((np.linspace(0,1,dst.shape[i])*(src.shape[i]-1))).astype(int)
        src_indices.append(z)

    nd = [0,]*(len(kernel.shape))
    for index in np.ndindex(dst.shape):
        dims = []
        # Are we starting a new dimension ?
        if index[-1] == 0:
            for i in range(len(index)-1,0,-1):
                if index[i]: break
                dims.insert(0,i-1)
        dims.append(len(dst.shape)-1)
        for dim in dims:
            i = index[dim]

            if toric:
                z = (indices[dim][dim] - src.shape[dim]//2 +(kernel.shape[dim]+1)%2 + src_indices[dim][i]) % src.shape[dim]
            else:
                z = (indices[dim][dim] - src.shape[dim]//2 +(kernel.shape[dim]+1)%2 + src_indices[dim][i])
            n = np.where((z >= 0)*(z < src.shape[dim]))[0]
            if dim == 0:
                nd[dim] = n.copy()
            else:
                nd[dim] = nd[dim-1][n]
            indices[dim+1] = np.take(indices[dim], n, 1)
            indices[dim+1][dim] = z[n]
        dim = len(dst.shape)-1
        z = indices[dim+1]
        R.extend( [dst_index,]*len(z[0]) )
        C.extend( (z*to_flat_index).sum(0).tolist() )
        D.extend( data[nd[-1]].tolist() )
        dst_index += 1

    return sp.coo_matrix( (D,(R,C)), (dst.size,src.size)).tocsr()


# Parameters from http://www.aliensaint.com/uo/java/rd/
# -----------------------------------------------------
n  = 256
dt = 1
t  = 25000
# Du, Dv, F, k = 0.16, 0.08, 0.035, 0.065 # Bacteria 1
# Du, Dv, F, k = 0.14, 0.06, 0.035, 0.065 # Bacteria 2
# Du, Dv, F, k = 0.16, 0.08, 0.060, 0.062 # Coral
# Du, Dv, F, k = 0.19, 0.05, 0.060, 0.062 # Fingerprint
# Du, Dv, F, k = 0.10, 0.10, 0.018, 0.050 # Spirals
# Du, Dv, F, k = 0.12, 0.08, 0.020, 0.050 # Spirals Dense
# Du, Dv, F, k = 0.10, 0.16, 0.020, 0.050 # Spirals Fast
# Du, Dv, F, k = 0.16, 0.08, 0.020, 0.055 # Unstable
# Du, Dv, F, k = 0.16, 0.08, 0.050, 0.065 # Worms 1
# Du, Dv, F, k = 0.16, 0.08, 0.054, 0.063 # Worms 2
# Du, Dv, F, k = 0.16, 0.08, 0.035, 0.060 # Zebrafish

Du, Dv, F, k = 0.16, 0.08, 0.054, 0.063 # http://mrob.com/pub/comp/xmorphia/F540/F540-k630.html
Du, Dv, F, k = 0.16, 0.08, 0.038, 0.063 # http://mrob.com/pub/comp/xmorphia/F380/F380-k630.html
Du, Dv, F, k = 0.16, 0.08, 0.037, 0.063 # 
Du, Dv, F, k = 0.16, 0.08, 0.046, 0.061 # http://mrob.com/pub/comp/xmorphia/F460/F460-k610.html
Du, Dv, F, k = 0.16, 0.08, 0.070, 0.061 # http://mrob.com/pub/comp/xmorphia/F700/F700-k610.html
Du, Dv, F, k = 0.16, 0.08, 0.066, 0.063 # http://mrob.com/pub/comp/xmorphia/F660/F660-k630.html
Du, Dv, F, k = 0.16, 0.08, 0.026, 0.061 # http://mrob.com/pub/comp/xmorphia/F260/F260-k610.html
Du, Dv, F, k = 0.16, 0.08, 0.086, 0.059 # http://mrob.com/pub/comp/xmorphia/F860/F860-k590.html

from optparse import OptionParser

defaults = dict(F=F, k=k, size=n, file='u.png')

parser = OptionParser()
parser.set_defaults(**defaults)

parser.add_option('-F', '--F', dest='F', type='float',
                  help='Parameter F, default %(F).3f.' % defaults)

parser.add_option('-k', '--k', dest='k', type='float',
                  help='Parameter k, default %(k).3f.' % defaults)

parser.add_option('--size', dest='size', type='int',
                  help='Image size, default %(size)d.' % defaults)

parser.add_option('--file', dest='file',
                  help='Output image file, default %(file)s.' % defaults)

options, args = parser.parse_args()

dim = (options.size, options.size)

u = np.zeros(dim, dtype = np.float32)
v = np.zeros(dim, dtype = np.float32)
U = np.zeros(dim, dtype = np.float32)
V = np.zeros(dim, dtype = np.float32)
Z = U*V*V
K = convolution_matrix(Z,Z, np.array([[np.NaN,  1., np.NaN], 
                                      [  1.,   -4.,   1.  ],
                                      [np.NaN,  1., np.NaN]]))
Lu = (K*U.ravel()).reshape(U.shape)
Lv = (K*V.ravel()).reshape(V.shape)

r = 20
u[...] = 1.0
v[...] = 0.0

for (x, y) in product(range(0, options.size, 64), repeat=2):
    u[x:x+8,y:y+8] = 0.50
    v[x:x+8,y:y+8] = 0.25

u += 0.05*np.random.random(dim)
v += 0.05*np.random.random(dim)
U[...] = u
V[...] = v

def on_idle(steps):
    global u,v,U,V,Z,Du,Dv,options
    for i in range(steps):
        if (i % 100) == 0:
            print >> stderr, (steps - i)/100,
        Lu = (K*U.ravel()).reshape(U.shape)
        Lv = (K*V.ravel()).reshape(V.shape)
        u += dt * (Du*Lu - Z + options.F * (1-U))
        v += dt * (Dv*Lv + Z - (options.F+options.k) * V)
    #U,V = np.maximum(u,0), np.maximum(v,0)
        U,V = u, v
        Z = U*V*V
    print >> stderr, ''

print u.max(), u.min()
on_idle(t)
print u.max(), u.min()

import Blit
Blit.utils.chan2img(u).save(options.file)
