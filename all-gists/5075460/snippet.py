# -*- encoding: utf-8 -*-
""" threadpool module, export ThreadPool class that is a non blocking
Thread Queue. Most important is that ThreadPool.add_task runs
asychroniousally. This method doesn't block process.

Example:
    p = ThreadPool(2)
    p.add_task(f1, arg1, arg2, test=False)
    p.add_task(f1, arg2, arg3, test=False)
    p.add_task(f1, arg4, arg5, test=True)
    p.add_task(f1, arg9, argX, test=False)
    print 'tasks added, wait for completion'
    p.wait_completion()

"f1" is a function that get 3 arguments.
This launches 2 Threads and add 4 calls in a Queue. Each p.add_task doesn't block execution.

:license: BSD
"""
__author__="Patrice Ferlet <metal3d@gmail.com>"

import logging
from threading import Thread
from Queue import Queue


class ThreadPool:
    """ Non blocking ThreadPool. Add Task to unlimited size
    Queue then reinsert content in limited Queue. 
    You should use wait_completion to wait the end of precesses
    """
    class _ThreadQueue(Thread):
        """ Internal class used as Worker
        """
        def __init__(self, pool, *args, **kwargs):
            """ Create the thread queue with unlimited poo
            """
            super(ThreadPool._ThreadQueue, self).__init__(*args, **kwargs)
            self.pool = pool.pool
            self.tasks = pool.tasks
            self.daemon = True
            self.start()

        def run(self):
            """ Run unlimited while Queues are not joined """
            while True:
                # reinsert the nonblocking queue 
                # in blocking queue, that should block
                # if queue is full
                self.tasks.put(self.pool.get(True))
                self.pool.task_done()
                #and read this queue...
                task,args,kwargs = self.tasks.get(True)
                try:
                    task(*args, **kwargs)
                except Exception, e:
                    logging.exception(e)
                finally:
                    self.tasks.task_done()
                

    def __init__(self, num=10):
        """ Create the thread queue with "num" thread in parallel

        :param num: number of workers to start
        :type num: integer
        """
        self.tasks = Queue(num)
        self.pool = Queue()

        for _ in range(num):
            self._ThreadQueue(self)

    def add_task(self, target, *args, **kwargs):
        """ Write in unlimited size queue which will be
        read in "run" method of a thread
        That should not block !

        :param target: function to start as thread
        :param args: argument tuple to pass to target
        :param kwargs: named arguments to pass to target
        """
        self.pool.put((target, args, kwargs))


    def wait_completion(self):
        """ Wait for the all threads to be completed """
        self.tasks.join()
        self.pool.join()