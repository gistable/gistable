import heapq
from threading import Lock


class HeapQueue(object):
    def __init__(self, values=None, maxsize=None, reversed=False):
        """
        Create a new heap queue.

        - ``maxsize`` will create a capped queue.
        - ``reversed`` will create a max heap queue (default is min).

        >>> queue = HeapQueue(maxsize=10, reversed=True)
        >>> queue.push('foo', 3)
        >>> queue.push('bar', 1)
        >>> queue.push('baz', 2)

        >>> # default behavior is to exhaust the queue
        >>> results = queue.sorted(exhaust=True)
        [(3, 'foo'), ('2, 'bar'), (1, 'baz')]

        >>> # the queue now has been exhausted
        >>> len(queue)
        0
        """
        self.lock = Lock()
        self.lst = values or []
        self.maxsize = maxsize
        self.reversed = reversed
        heapq.heapify(self.lst)

    def __len__(self):
        return len(self.lst)

    def push(self, element, score):
        if not self.reversed:
            score = score * -1

        element = (score, element)

        with self.lock:
            if self.maxsize and len(self.lst) >= self.maxsize:
                heapq.heappushpop(self.lst, element)
            else:
                heapq.heappush(self.lst, element)

    def pop(self):
        with self.lock:
            score, element = heapq.heappop(self.lst)
        if self.reversed:
            score = score * -1
        return score, element

    def sorted(self):
        with self.lock:
            results = [heapq.heappop(self.lst) for x in xrange(len(self.lst))]

        for score, element in reversed(results):
            if not self.reversed:
                score = score * -1
            yield score, element


if __name__ == '__main__':
    # test min heap queue
    queue = HeapQueue(maxsize=2)
    queue.push('foo', 3)
    queue.push('bar', 1)
    queue.push('baz', 2)
    results = list(queue.sorted())
    assert len(results) == 2
    assert results[0] == (1, 'bar'), results[0]
    assert results[1] == (2, 'baz'), results[1]

    # test max heap queue
    queue = HeapQueue(maxsize=2, reversed=True)
    queue.push('foo', 3)
    queue.push('bar', 1)
    queue.push('baz', 2)
    results = list(queue.sorted())
    assert len(results) == 2
    assert results[0] == (3, 'foo'), results[0]
    assert results[1] == (2, 'baz'), results[1]
