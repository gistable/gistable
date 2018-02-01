"""
Implement a queue with two stacks

Interview practice from coding for interviews - March 2014
"""

class Staqueue(object):
    """ Implements a queue with two stacks 

    One stack is used for enqueing, and the other dequeing.  If an enqueue is requested
    while the dequeue stack is populated, all items are popped from the dequeue stack and
    pushed onto the enqueue stack before performing the enqueue, and vice-versa.

    The run-time of enqueue and dequeue varies between O(N) when the prior operation was
    different, and O(1) when the prior operation was the same.  The run-time on a random
    sequence of M enqueue and dequeue operations is O(M) as the O(N) operations are
    amortized over the O(1) operations.

    The additional space requirement for tracking the minimum is O(1), only the minimum
    itself is stored.  dequeue can now sometimes require two passes and leave the Staqueue
    in the enqueue state, but is still O(N) amortized over all dequeue operations.
    """
    def __init__(self):
        self.in_stack = []
        self.out_stack = []
        self._minimum = None

    def enqueue(self, val):
        while self.out_stack:
            self.in_stack.append(self.out_stack.pop())
        self.in_stack.append(val)
        self._set_if_minimum(val)

    def dequeue(self):
        while self.in_stack:
            self.out_stack.append(self.in_stack.pop())
        if not self.out_stack:
            return None
        v = self.out_stack.pop()
        if self.minimum == v:
            self.minimum = None
            # find a new minimum as we might have just dequeued our current minimum
            while self.out_stack:
                n = self.out_stack.pop()
                self._set_if_minimum(n)
                self.in_stack.append(n)
        return v

    def _set_if_minimum(self, x):
        if not self._minimum or x < self._minimum:
            self._minimum = x

    def minimum(self):
        return self._minimum

if __name__ == '__main__':
    test1 = [1, 2, 3]
    staque = Staqueue()
    for v in test1:
        staque.enqueue(v)
    while True:
        v = staque.dequeue()
        if not v:
            break
        print "next: " + str(v)
        print "minimum: " + str(staque.minimum())

