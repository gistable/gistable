#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple script illustrating how to perform embarrassingly parallel computations
in Python using MPI/mpi4py. I like this approach a lot as its very easy to get
right without having to deal with the complications arising from forked
processes which the multiprocessing module uses.

This script can be executed with or without `mpirun`; it will just run on one
core if not executed with it. With some more logic its also possible to make
MPI/mpi4py completely optional.


Run with (making sure MPI and mpi4py are installed):

$ mpirun -n X python embarrassingly_parallel.py

where X is the number of processes you want to run this on.


The MIT License (MIT)

Copyright (c) 2015 Lion Krischer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from mpi4py import MPI

# Use default communicator. No need to complicate things.
COMM = MPI.COMM_WORLD


def split(container, count):
    """
    Simple function splitting a container into equal length chunks.

    Order is not preserved but this is potentially an advantage depending on
    the use case.
    """
    return [container[_i::count] for _i in range(count)]


# Collect whatever has to be done in a list. Here we'll just collect a list of
# numbers. Only the first rank has to do this.
if COMM.rank == 0:
    jobs = list(range(100))
    # Split into however many cores are available.
    jobs = split(jobs, COMM.size)
else:
    jobs = None

# Scatter jobs across cores.
jobs = COMM.scatter(jobs, root=0)

# Now each rank just does its jobs and collects everything in a results list.
# Make sure to not use super big objects in there as they will be pickled to be
# exchanged over MPI.
results = []
for job in jobs:
    # Do something meaningful here...
    results.append(job ** 2)

# Gather results on rank 0.
results = MPI.COMM_WORLD.gather(results, root=0)

if COMM.rank == 0:
    # Flatten list of lists.
    results = [_i for temp in results for _i in temp]

    print("Results:", results)
