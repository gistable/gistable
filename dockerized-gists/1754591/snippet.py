try:
    # for Python 2.x
    from Queue import Queue
except ImportError:
    # for Python 3.x
    from queue import Queue
from threading import Thread, Event

import random
import sys
import time

class BusyBee(object):

    def __init__(self):
        self._progress = 0

        self.queue = Queue(1)   # used to communicate progress to the thread
        self.event = Event()    # used to tell the thread when to finish
        self.progress_bar = Thread(target=self.print_progress, args=(self.event, self.queue))
        self.progress_bar.start()

    def print_progress(self, e, q):
        """Updates a progress bar on stdout anytime progress is made"""

        while True:
            if e.is_set():
                # if our event is set, break out of the infinite loop and
                # prepare to terminate this thread
                break

            while not q.full():
                # wait for more progress to be made
                time.sleep(0.1)

            # get the current progress value
            p = q.get()

            # print the current progress value in bar and percent form
            sys.stdout.write('\r[%s] %s%%' % (('#' * int(p / 2)).ljust(50, ' '), int(p)))
            sys.stdout.flush()

    @property
    def progress(self):
        """Returns the current progress value"""

        return self._progress

    @progress.setter
    def progress(self, value):
        """Sets the current progress value, passing updates to the thread"""

        value = min(value, 100)
        self._progress = value

        # this is the key to this solution
        self.queue.put(self._progress)

    def __call__(self):
        """Simulates some progress being made on something"""

        while True:
            if self.progress >= 100:
                # we don't want more than 100%
                break

            time.sleep(0.2)
            r = random.randint(0, 5)

            # make some progress
            self.progress += r

        # reached 100%; kill the thread and exit
        self.event.set()
        self.progress_bar.join()
        sys.exit(0)

if __name__ == '__main__':
    b = BusyBee()
    b()