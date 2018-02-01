#!/usr/bin/env python
"""
Standard Master/Slave design in mpi4py, collects results in a list and pickles them to a file.
"""
import ROOT
 
from mpi4py import MPI
import sys
import cPickle as pick
 
WORKTAG = 0
DIETAG = 1
 
class Work():
    def __init__(self, work_items):
        self.work_items = work_items[:] 
 
    def get_next_item(self):
        if len(self.work_items) == 0:
            return None
        return self.work_items.pop()
 
def master(wi):
    all_data = []
    size = MPI.COMM_WORLD.Get_size()
    current_work = Work(wi) 
    comm = MPI.COMM_WORLD
    status = MPI.Status()
    for i in range(1, size): 
        anext = current_work.get_next_item() 
        if not anext: break
        comm.send(obj=anext, dest=i, tag=WORKTAG)
 
    while 1:
        anext = current_work.get_next_item()
        if not anext: break
        data = comm.recv(obj=None, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        all_data.append(data)
        comm.send(obj=anext, dest=status.Get_source(), tag=WORKTAG)
 
    for i in range(1,size):
        data = comm.recv(obj=None, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        all_data.append(data)
    
    for i in range(1,size):
        comm.send(obj=None, dest=i, tag=DIETAG)
     
    return all_data
        
    
def slave(do_work):
    comm = MPI.COMM_WORLD
    status = MPI.Status()
    while 1:
        data = comm.recv(obj=None, source=0, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag(): break
        comm.send(obj=do_work(data), dest=0)
    
def main(work_list, do_work):
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    size = MPI.COMM_WORLD.Get_size() 
    
    if rank == 0:
        all_dat = master(work_list)
    else:
        slave(do_work)
 