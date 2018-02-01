from gevent import monkey
monkey.patch_all()
import gevent.pool

import os
import random
import time
import datetime
from multiprocessing import Semaphore, Array


class BaseWorker(object):

    def work(self):
        while True:
            self.spawn_child()

    def spawn_child(self):
        raise NotImplementedError('Implement this in a subclass.')

    def fake_work(self):
        sleep_time = 3 * random.random()
        print datetime.datetime.now(), '- Hello from', os.getpid(), '- %.3fs' % sleep_time
        time.sleep(sleep_time)



class ForkingWorker(BaseWorker):

    def __init__(self, num_processes=1):
        # Set up sync primitives, to communicate with the spawned children
        self._semaphore = Semaphore(num_processes)
        self._slots = Array('i', [0] * num_processes)

    def spawn_child(self):
        """Forks and executes the job."""
        self._semaphore.acquire()    # responsible for the blocking

        # Select an empty slot from self._slots (the first 0 value is picked)
        # The implementation guarantees there will always be at least one empty slot
        for slot, value in enumerate(self._slots):
            if value == 0:
                break

        # The usual hardcore forking action
        child_pid = os.fork()
        if child_pid == 0:
            random.seed()
            # Within child
            try:
                self.fake_work()
            finally:
                # This is the new stuff.  Remember, we're in the child process
                # currently. When all work is done here, free up the current
                # slot (by writing a 0 in the slot position).  This
                # communicates to the parent that the current child has died
                # (so can safely be forgotten about).
                self._slots[slot] = 0
                self._semaphore.release()
                os._exit(0)
        else:
            # Within parent, keep track of the new child by writing its PID
            # into the first free slot index.
            self._slots[slot] = child_pid


class GeventWorker(BaseWorker):

    def __init__(self, num_processes=1):
        self._pool = gevent.pool.Pool(num_processes)

    def spawn_child(self):
        """Forks and executes the job."""
        self._pool.spawn(self.fake_work)


if __name__ == '__main__':
    #fw = ForkingWorker(4)
    #fw.work()

    gw = GeventWorker(4)
    gw.work()
