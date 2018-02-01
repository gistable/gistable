#!/usr/bin/env python
import os
import itertools
import multiprocessing as mp
from math import ceil
from types import GeneratorType as generator
from functools import partial
from time import time


class MapReduceTask(object):
    ''' 
      workers=2, mapper=None, prefiltering=None, 
      postfiltering=None, reducer=None, initializer=[] 
    '''
    def __init__(self, **kwargs):
        defaults = {
            'workers'       : 2,           # Number of processes to be spawned
            'mapper'        : None,        # function to apply to items
            'prefiltering'  : None,        # function to filter items before entering map phase
            'postfiltering' : None,        # function to filter items after map phase
            'reducer'       : None,        # function passed to reduce for the reduce phases (also the final phase)
            'initializer'   : None,        # initializer value passed only the final reduce phase
            'worker_assign' : None,        # function to assign items to workers (used for generators only)
        }
        defaults.update(kwargs)
        self.__dict__.update(defaults)


class MapReducer(object):
    def __init__(self, iterable, **kwargs):
        self.started = time()
        self.Iterable = iterable
        self.MR_Manager = None
        self.MR_Task = MapReduceTask(**kwargs)

    def mapper(self, item):
        ''' add any extra handling for the map phase here '''
        return self.MR_Task.mapper(item)
    
    def process(self, items, manager):
        itemlist = items
        if not self.MR_Task.prefiltering is None:
            itemlist = itertools.ifilter(self.MR_Task.prefiltering, itemlist)
        itemlist = itertools.imap(self.mapper, itemlist)
        if not self.MR_Task.postfiltering is None:
            itemlist = itertools.ifilter(self.MR_Task.postfiltering, itemlist)
        if self.MR_Task.reducer is None:
            manager.extend(list(itemlist))
        else:
            ''' chain will resolve the issue of non-uniform return values '''
            manager.append(reduce(self.MR_Task.reducer, itemlist, self.MR_Task.initializer))
      
    def run(self):
        m = mp.Manager()
        ''' manager object to store the result from all processes '''
        self.MR_Manager = m.list()
        processes = []
        step = None
        if not isinstance(self.Iterable, generator) and not isinstance(self.Iterable, xrange):
            ''' Lists, tuples (not generators) '''
            l = len(self.Iterable)
            ''' determine slice size '''
            step = int(ceil(l/float(self.MR_Task.workers)))
        ''' setup processes '''
        for n in range(self.MR_Task.workers):
            ''' if the length of the iterable is known slice the iterable and assign to each worker '''
            if step is not None:
                P = mp.Process(target=self.process, args=(itertools.islice(self.Iterable, n*step, (n+1)*step), self.MR_Manager))
            else:
                ''' 
                create a partial since we need to pass the worker count and 
                current worker id to the assignment filter 
                '''
                assignment = partial(self.MR_Task.worker_assign, self.MR_Task.workers, n)
                ''' otherwise filter elements with worker_assign '''
                P = mp.Process(target=self.process, args=(itertools.ifilter(assignment, self.Iterable,), self.MR_Manager))
            processes.append(P)
        ''' start & run '''
        [ p.start() for p in processes ]
        [ p.join()  for p in processes ]
        ''' final reduce phase ''' 
        itemlist = itertools.chain(self.MR_Manager)
        if not self.MR_Task.reducer is None:
            ''' reduce cannot handle None initializer, but works as expected if we omit the parameter altogether '''
            if not self.MR_Task.initializer is None:
                return reduce(self.MR_Task.reducer, itemlist, self.MR_Task.initializer)
            else:
                return reduce(self.MR_Task.reducer, itemlist)        
        else:
            return itemlist


if __name__ == "__main__":
    ''' Helper Functions for the examples '''
    def mapper_1(item):
        return -item

    def mapper_2(item):
        return item**2

    def reducer_2(accumulated, item):
        return accumulated + item

    def filter_1(item):
        return item % 2 == 0

    def timer(start):
        print '  Time       : %8.6fsec' % (time()-start)  
      
    N = 20
    ''' Example '''
    start = time()
    mr = MapReducer(range(N), mapper=mapper_1)
    print '* map '
    print '  List:', list(mr.run())
    ''' approximate running time '''
    timer(mr.started)
    mr = MapReducer(range(N), mapper=mapper_2, reducer=reducer_2, initializer=0)
    print '* map & reduce '
    print '  MR Result  :', mr.run()
    timer(mr.started)
    print '  Validation :', sum([ n**2 for n in range(N) ])
    mr = MapReducer(range(N), mapper=mapper_2, reducer=reducer_2, prefiltering=filter_1, initializer=0)
    print '* pre-filtering, map, reduce '
    print '  MR Result  :', mr.run()
    timer(mr.started)
    print '  Validation :', sum([ n**2 for n in range(N) if n % 2 == 0 ])
    mr = MapReducer(
        xrange(N), 
        mapper=mapper_2, 
        reducer=reducer_2, 
        initializer=0, 
        prefiltering=filter_1, 
        worker_assign=lambda workers, current_worker_id, item: item % workers == current_worker_id
    )
    print '* pre-filtering, map, reduce with generator input '
    print '  MR Result  :', mr.run()
    timer(mr.started)
    print '  Validation :', sum([ n**2 for n in xrange(N) if n % 2 == 0 ])
        
