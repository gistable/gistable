import Queue as _oldQueue
import heapq
from time import mktime, time as _time

class PriorityQueue(_oldQueue.PriorityQueue):
    '''
    This class extends Python's Queue.PriorityQueue by allowing it to
    evict lower priority items in order to make room.  This avoids a 
    starvation problem where low-priority items fill the queue and prevent
    a high-priority item from being inserted.  
    '''

    def put(self, item, block=True, timeout=None, evict=False):
        """Put an item into the queue.

        If 'evict' is True, when the queue is full it will force an item
        of lower priority to be evicted to make room for this item rather 
        than blocking.  If the queue is full and there are no items of lower
        priority, then behavior is identical to Python's `Queue.Queue`.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if evict and self._qsize() == self.maxsize:
                    # Evict the oldest, lowest priority item from the queue, 
                    # iff it is lower priority than this item:
                    tail = heapq.nlargest(1, self.queue )
                    if item < tail: self.queue.remove(tail)

                elif not block:
                    if self._qsize() == self.maxsize: raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0: raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def put_nowait(self, item, evict=False):
        """Put an item into the queue without blocking.

        If 'evict' is True, make room by discarding a lower-priority entry
        if necessary (e.g. the queue is full).  Otherwise, only enqueue the 
        item if a free slot is immediately available.
        Otherwise raise the Full exception.
        """
        return self.put(item, block=False, evict=evict)


if __name__ == '__main__':
    q = PriorityQueue(1)
    q.put((5,'unimportant'))
    # kick out the low-priority item to make room!
    q.put_nowait((0,'higher priority!'), evict=True)
    priority,val = q.get()
    print priority == 0
    print val == 'higher priority!'
    