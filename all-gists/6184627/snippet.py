#!/usr/bin/env python
#coding:utf-8


import threading
from Queue import Queue


class ThreadPool(threading.Thread):

    def __init__(self, max_nu):
        threading.Thread.__init__(self)
        self.max_nu=max_nu
        self.task_pool=Queue(max_nu)
        self.runing_pool=[]
        self.setDaemon(True)
        self.start()

    def put(self, thread):
        self.task_pool.put(thread)

    def run(self):
        for i in xrange(self.max_nu):
            self.runing_pool.append(self.task_pool.get())
            try:
                self.runing_pool[i].start()
            except:
                print "is not a thread object instance"
        while True:
            for i in xrange(self.max_nu):
                if self.runing_pool[i].isAlive():
                    continue
                else:
                    self.runing_pool[i]=self.task_pool.get()
                    self.runing_pool[i].start()

            time.sleep(0.1)

    def wait_all(self):
        

class TaskThread(threading.Thread):
    def __init__(self, nu):
        threading.Thread.__init__(self)
        self.nu=nu
    def run(self):
        for i in xrange(10):
            print self.nu
            time.sleep(1) 


if __name__ == "__main__":

    thread_pool=ThreadPool(20)
    for i in xrange(100):
        t=TaskThread(i)
        thread_pool.put(t)
