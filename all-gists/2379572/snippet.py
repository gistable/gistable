import os
import tempfile
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

mode = MPI.MODE_RDONLY

if rank == 0:
    # get a list of the files to scatter
    #for f in glob.glob(args.alignments):
    work = ['test1.txt', 'test2.txt']
else:
    work = None

# scatter work units to nodes
unit = comm.scatter(work, root=0)
# ===================================
# This should be node-related work
# ===================================

# open the file on a node
f = MPI.File.Open(comm, unit, mode)
# create a buffer for the data of size f.Get_size()
ba = bytearray(f.Get_size())
# read the contents into a byte array
f.Iread(ba)
# close the file
f.Close()
# write buffer to a tempfile
descriptor, path = tempfile.mkstemp(suffix='mpi.txt')
print path
tf = os.fdopen(descriptor, 'w')
tf.write(ba)
tf.close()
# get contents of tempfile
contents = open(path, 'rU').read() + str(comm.Get_rank())
os.remove(path)

# ===================================
# End of node-related work
# ===================================

# gather results
result = comm.gather(contents, root=0)
# do something with result
if rank == 0:
    print result
else:
    result = None