# !/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import Queue
import threading
import traceback

class ExitException(Exception):
    pass

class Work(threading.Thread):
    def __init__(self, inqueue, killall=None):
        threading.Thread.__init__(self)
        self.exit = threading.Event()
        self._inqueue = inqueue
        self._killall = killall
        self._get = inqueue.get
        self.daemon = True
        self.init()
        self.start()

    def run(self):
        while not self.exit.is_set():
            try:
                args = self._get(timeout=0.2)
            except Queue.Empty:
                continue

            try:
                self.do(args)
            except ExitException, e:
                self._killall.set()
            except Exception, e:
                traceback.print_exc()
            finally:
                self._inqueue.task_done()

    def init(self):
        pass

    def do(self, args):
        pass

class WorkManager(object):
    def __init__(self, processes=2, worker=Work):
        self._inqueue = Queue.Queue()
        self._put = self._inqueue.put
        self._killall = threading.Event()
        self.killed = False
        self.worker = worker

        self._pool = []
        self._processes = processes
        self._repopulate_pool()

    def _repopulate_pool(self):
        for i in range(self._processes - len(self._pool)):
            self._pool.append(self.worker(self._inqueue, self._killall))

    def apply(self, args):
        self.apply_async(args)
        self.wait()

    def apply_async(self, args):
        self._put(args)#任务入队，Queue内部实现了同步机制

    def map(self, iterable):
        self.map_async(iterable)
        self.wait()

    def map_async(self, iterable):
        for each in iterable:
            self.apply_async(each)

    def wait(self):
        try:
            while not self._inqueue.empty():
                time.sleep(0.1)
                _break = True
                for t in self._pool:
                    if t.isAlive():
                        _break = False
                        break
                if _break: break
                if self._killall.is_set(): raise KeyboardInterrupt
            self._inqueue.join()
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            for t in self._pool:
                if t: t.exit.set()
            for t in self._pool:
                if t: t.join(1)
            raise

    def __len__(self):
        return len(self._inqueue)

if __name__ == '__main__':
    import logging
    logging.basicConfig(format="[TN:%(threadName)s] %(message)s", level=logging.INFO)
    class test_work(Work):
        def init(self):
            print self

        def do(self, args):
            logging.info(args)
            time.sleep(0.1)
            if args == 600:
                raise ExitException

    start = time.time()
    work_manager =  WorkManager(10, worker=test_work)#或者work_manager =  WorkManager(10000, 20)
    work_manager.map(range(1000))
    work_manager.map(range(1000))
    end = time.time()
    print "cost all time: %s" % (end-start)
