#!/usr/bin/env python

"""
Allocate a GPUArray in one process and access it in another process using IPC
handles.
"""

import multiprocessing as mp
import numpy as np
import zmq

import pycuda.driver as drv
import pycuda.gpuarray as gpuarray

def proc1():
    sock = zmq.Context().socket(zmq.REQ)
    sock.connect('tcp://localhost:5000')

    drv.init()
    dev = drv.Device(0)
    ctx = dev.make_context()

    x_gpu = gpuarray.to_gpu(np.random.rand(8))
    h = drv.mem_get_ipc_handle(x_gpu.ptr)
    sock.send_pyobj((x_gpu.shape, x_gpu.dtype, h))
    sock.recv_pyobj()

    ctx.detach()

def proc2():
    sock = zmq.Context().socket(zmq.REP)
    sock.bind('tcp://*:5000')

    drv.init()
    dev = drv.Device(0)
    ctx = dev.make_context()

    shape, dtype, h = sock.recv_pyobj()
    sock.send_pyobj('')

    x_gpu = gpuarray.GPUArray(shape, dtype, gpudata=drv.IPCMemoryHandle(h))
    print x_gpu

    ctx.detach()
    
if __name__ == '__main__':
    p1 = mp.Process(target=proc1)
    p2 = mp.Process(target=proc2)

    p1.start()
    p2.start()
