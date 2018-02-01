"""

This code computes pi. It's not the first python
pi computation tool that I've written.  This program
is a good test of the mpi4py library, which is
essentially a python wrapper to the C MPI library.

To execute this code:

mpiexec -np NUMBER_OF_PROCESSES -f NODES_FILE python mpipypi.py

where....

NUMBER_OF_PROCESSES is the number of desired processes.
NODES_FILE is a file which records the location of your nodes.

""" 

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

slice_size = 1000000
total_slices = 50

# This is the master node.
if rank == 0:
    pi = 0
    slice = 0
    process = 1

    print size

    # Send the first batch of processes to the nodes.
    while process < size and slice < total_slices:
        comm.send(slice, dest=process, tag=1)
        print "Sending slice",slice,"to process",process
        slice += 1
        process += 1

    # Wait for the data to come back
    received_processes = 0
    while received_processes < total_slices:
        pi += comm.recv(source=MPI.ANY_SOURCE, tag=1)
        process = comm.recv(source=MPI.ANY_SOURCE, tag=2)
        print "Recieved data from process", process
        received_processes += 1

        if slice < total_slices:
            comm.send(slice, dest=process, tag=1)
            print "Sending slice",slice,"to process",process
            slice += 1

    # Send the shutdown signal
    for process in range(1,size):
        comm.send(-1, dest=process, tag=1)

    print "Pi is ", 4.0 * pi

# These are the slave nodes, where rank > 0. They do the real work
else:
    while True:
        start = comm.recv(source=0, tag=1)
        if start == -1: break

        i = 0
        slice_value = 0
        while i < slice_size:
            if i%2 == 0:
                slice_value += 1.0 / (2*(start*slice_size+i)+1)
            else:
                slice_value -= 1.0 / (2*(start*slice_size+i)+1)
            i += 1

        comm.send(slice_value, dest=0, tag=1)
        comm.send(rank, dest=0, tag=2)
