#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SPHERE SCENE RAY TRACER

This is a basic port of the simple ray tracer from Chapter 6 of
"CUDA by Example", by Sanders and Kandrot. With a few exceptions
(notably, the `hit()` method is not bound to a struct containing 
sphere data and we use a numpy record array).

On my GeForce GTX 750ti, the kernel computes in ~180 microseconds,
and the entire operation including data transfers takes about 
100 milliseconds. That's ~0.2x the speed of the pure CUDA 
implementation.

Author: Daniel Rothenberg <darothen@mit.edu>

"""

import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

from numbapro import cuda, int16, float32, from_dtype
from timeit import default_timer as timer

DIM     = 2048  # domain width, in pixels
DM      = min([DIM, 1000]) # constraint for sphere locations
SPHERES = 200   # number of spheres in scene
INF     = 2e10  # really large number
VERBOSE = False # print out some debug stuff along the way

# Randomly generate a number between [0, x)
rnd = lambda x: x*np.random.rand()

# A numpy record array (like a struct) to record sphere data
Sphere = np.dtype([
    # RGB color values (floats from [0, 1])
    ('r', 'f4'),  ('g', 'f4'), ('b', 'f4'), 
    # sphere radius 
    ('radius', 'f4'),
    # sphere (x, y, z) coordinates 
    ('x', 'f4'),  ('y', 'f4'), ('z', 'f4'),], align=True) 
Sphere_t = from_dtype(Sphere) # Create a type that numba can recognize!

# We can use that type in our device functions and later the kernel!
@cuda.jit(restype=float32, argtypes=[float32, float32, Sphere_t], 
          device=True, inline=False)
def hit(ox, oy, sph):
    """ Compute whether a ray parallel to the z-axisoriginating at 
    (ox, oy, INF) will intersect a given sphere; if so, return the 
    distance to the surface of the sphere.
    """
    dx = ox - sph.x
    dy = oy - sph.y
    rad = sph.radius
    if ( dx*dx + dy*dy < rad*rad ):
        dz = sqrt( rad*rad - dx*dx - dy*dy )
        return dz + sph.z
    else:
        return -INF

@cuda.jit(argtypes=(Sphere_t[:], int16[:,:,:]))
def kernel(spheres, bitmap):
 
    x, y = cuda.grid(2) # alias for threadIdx.x + ( blockIdx.x * blockDim.x ),
                        #           threadIdx.y + ( blockIdx.y * blockDim.y )
    # shift the grid to [-DIM/2, DIM/2]
    ox = x - DIM/2
    oy = y - DIM/2

    r = 0. 
    g = 0.
    b = 0.
    maxz = -INF

    i = 0 # emulate a C-style for-loop, exposing the idx increment logic
    while (i < SPHERES):
        t = hit(ox, oy, spheres[i])
        rad = spheres[i].radius

        if (t > maxz):
            dz = t - spheres[i].z # t = dz + z; inverting hit() result
            n = dz / sqrt( rad*rad )
            fscale = n # shades the color to be darker as we recede from 
                       # the edge of the cube circumscribing the sphere

            r = spheres[i].r*fscale
            g = spheres[i].g*fscale
            b = spheres[i].b*fscale
            maxz = t
        i += 1

    # Save the RGBA value for this particular pixel
    bitmap[x,y,0] = int(r*255.)
    bitmap[x,y,1] = int(g*255.)
    bitmap[x,y,2] = int(b*255.)
    bitmap[x,y,3] = 255

if __name__ == "__main__":

    start = timer()

    # Create a container for the pixel RGBA information of our image
    bitmap = np.zeros([DIM, DIM, 4], dtype=np.int16)
   
    # Copy to device memory 
    d_bitmap = cuda.to_device(bitmap)
    # Create empty container for our Sphere data on device
    d_spheres = cuda.device_array(SPHERES, dtype=Sphere_t)

    # Create an empty container of spheres on host, and populate it
    # with some random data.
    temp_spheres = np.empty(SPHERES, dtype=Sphere_t)
    for i in xrange(SPHERES):
        temp_spheres[i]['r'] = rnd(1.0)
        temp_spheres[i]['g'] = rnd(1.0)
        temp_spheres[i]['b'] = rnd(1.0)
        temp_spheres[i]['x'] = rnd(DIM) - DIM/2
        temp_spheres[i]['y'] = rnd(DIM) - DIM/2
        temp_spheres[i]['z'] = rnd(DIM) - DIM/2
        temp_spheres[i]['radius'] = rnd(100.0) + 20  

        if VERBOSE:
            sph = temp_spheres[i]
            print "Sphere %d" % i
            print "\t(r,g,b)->(%1.2f,%1.2f,%1.2f)" % (sph['r'], sph['b'], sph['g'])
            print "\t(x,y,z)->(%4.1f,%4.1f,%4.1f)" % (sph['x'], sph['y'], sph['z'])
            print "\tradius->%3.1f" % sph['radius']
    # Copy the sphere data to the device
    cuda.to_device(temp_spheres, to=d_spheres) 

    # Here, we choose the granularity of the threading on our device. We want
    # to try to cover the entire image with simulatenous threads, so we'll 
    # choose a grid of (DIM/16. DIM/16) blocks, each with (16, 16) threads
    grids = (DIM/16, DIM/16)
    threads = (16, 16)

    # Execute the kernel
    kernel[grids, threads](d_spheres, d_bitmap)
    kernel_dt = timer() - start

    # Copy the result from the kernel ordering the ray tracing back to host
    bitmap = d_bitmap.copy_to_host()
    mem_dt = timer() - start

    print "Elapsed time in"
    print "          kernel:  {:3.1f} µs".format(kernel_dt*1e6) 
    print "    device->host:  {:3.1f} ms".format(mem_dt*1e3) 

    # Visualize the resulting scene. We'll do this with two side-by-side plots:
    #    Left -> the scene rendered in psuedo-3D, accounting for sphere placement
    #   Right -> flat circle projections of spheres, in z-order looking down
    
    fig, axs = plt.subplots(1, 2, figsize=(12,6))

    bitmap = np.transpose(bitmap/255., (1, 0, 2)) # swap image's x-y axes
    axs[0].imshow(bitmap)
    axs[0].grid(False)

    # sort the spheres by Z for visualizing z-level order, plot using circle artists
    temp_spheres.sort(order='radius')
    for i in xrange(SPHERES):
        sph = temp_spheres[-i] # temp_spheres is actually backwards!
        circ = plt.Circle((sph['x']+DIM/2, sph['y']+DIM/2), sph['radius'],
                          color=(sph['r'], sph['g'], sph['b']))
        axs[1].add_artist(circ)
    
    for ax in axs:
        ax.set_xlim(0, DIM)
        ax.set_ylim(0, DIM)

    plt.show()
