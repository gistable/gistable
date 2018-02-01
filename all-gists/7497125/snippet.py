"""
An asynchronous task manager.

This is a simple implementation for background task handing. No guarentees are
provided for task execution.

This was developed in the course of the work don for the victims project and 
that version is available at 
https://github.com/victims/victims-web/blob/master/src/victims_web/handlers/task.py

A usage example would be:
>>> from <task-module> import taskman
>>> taskman.add_task(my_awesome_method, arg1, arg2)
"""

from multiprocessing import Process
from threading import Thread
from Queue import Queue


class TaskException(Exception):
    pass


class Waiter(Thread):
    """
    Waiter thread
    """
    def __init__(self):
        self.__q = Queue()
        self.__stopped = False

    @property
    def stopped(self):
        return self.__stopped

    def run(self):
        while True:
            child = self.__q.get()
            if child is None:
                return
            child.join()

    def waiton(self, process):
        self.__q.put(process)

    def stop(self):
        self.__q.put(None)
        self.__stopped = True


class TaskManager():
    """
    Task Manager implementation. This class allows for any function to be fired
    as their own process. Once fired the parent procsses can continue on doing
    their business.

    We do not guarentee execution of success of process.
    """
    def __init__(self):
        self._waiter = Waiter()

    def __del__(self):
        self._waiter.stop()

    def add_task(self, fn, *args):
        """
        If the kitchen is still accepting orders place task on waiter's docket.
        Else, a TaskException is raised.

        :Parameters:
            `fn`: Target function to run as a seperate Process
            `args`: The arguments to pass to the target function
        """
        if self._waiter.stopped:
            raise TaskException('We are close for business. Go elsewhere!')
        process = Process(target=fn, args=args)
        process.start()
        self._waiter.waiton(process)


taskman = TaskManager()