#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A simple thread pool.

@author: Junaid P V
@license: GPLv3
"""
    
from threading import Thread, RLock, Lock
from time import sleep
from functools import wraps

def synchronous( tlockname ):
    """
    A decorator to place an instance based lock around a method
    from: http://code.activestate.com/recipes/577105-synchronization-decorator-for-class-methods/
    """

    def _synched(func):
        @wraps(func)
        def _synchronizer(self,*args, **kwargs):
            tlock = self.__getattribute__( tlockname)
            tlock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                tlock.release()
        return _synchronizer
    return _synched

class ThreadPoolThread(Thread):
    
    def __init__(self, pool):
        Thread.__init__(self)
        self.__pool = pool
        self.start()
    def run(self):
        try:
            while True:
                task = self.__pool.pop_task()
                if task == None:
                    break
                if task[1] != None and task[2] != None:
                    task[0](*task[1], **task[2])
                elif task[1] != None:
                    task[0](*task[1])
                else:
                    task[0]()
        finally:
            # Always inform about thread finish
            self.__pool.thread_finished()
    

class ThreadPool(object):
    
    def __init__(self, thread_count):
        self.__tasks = []
        self.task_lock = Lock()
        self.__thread_count = thread_count
        self.__threads = []
        self.threads_lock = Lock()
        self.__finished_threads_count = 0
        self.finished_threads_count_lock = Lock()
        
    @synchronous('task_lock')
    def add_task(self, callable_, args=None, kwds=None):
        self.__tasks.append((callable_, args, kwds))
    
    @synchronous('task_lock')
    def pop_task(self):
        if len(self.__tasks) > 0:
            return self.__tasks.pop(0)
        else:
            return None
    
    def start_workers(self):
        self.__finished_threads_count = 0
        self.__threads = []
        for i in range(self.__thread_count):
            worker = ThreadPoolThread(self)
            self.__threads.append(worker)
    
    def wait(self):
        """
        Wait for every worker threads to finish
        """
        while True:
            finished_threads_count = self.get_finished_threads_count()
            if finished_threads_count == self.__thread_count:
                break
            sleep(1)
    
    @synchronous('finished_threads_count_lock')
    def thread_finished(self):
        self.__finished_threads_count += 1
    
    @synchronous('finished_threads_count_lock')
    def get_finished_threads_count(self):
        return self.__finished_threads_count


"""
Example
"""
if __name__ == '__main__':
    from threading import current_thread


    class SampleTask:
        def __init__(self, name):
            self.name = name
        def call_me(self, count):
            print "Thread: ", current_thread().getName()
            for i in range(count):
                print self.name, ': counting ', i
                sleep(3)
    
    pool = ThreadPool(2)
    a = SampleTask("A")
    b = SampleTask("B")
    c = SampleTask("C")
    d = SampleTask("D")
    e = SampleTask("E")
    pool.add_task(a.call_me, (5,))
    pool.add_task(b.call_me, (7,))
    pool.add_task(c.call_me, (6,))
    pool.add_task(d.call_me, (4,))
    pool.add_task(e.call_me, (5,))
    pool.start_workers()
    pool.wait()
    print "Sleeping 5 seconds before next run..."
    sleep(5)
    f = SampleTask("F")
    g = SampleTask("G")
    h = SampleTask("H")
    pool.add_task(f.call_me, (5,))
    pool.add_task(g.call_me, (4,))
    pool.add_task(h.call_me, (3,))
    pool.start_workers()
    pool.wait()