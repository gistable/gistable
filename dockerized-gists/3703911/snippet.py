#!/usr/bin/python

import numpy.random as random
from bisect import bisect_left, bisect_right 

class SlaveNode:
    def __init__ (self, data):
        self.data = sorted(data)

    def get_range (self):
        return self.data[0], self.data[-1], len(self.data)

    def query_bound (self, k):
        l = bisect_left  (self.data, k)
        r = bisect_right (self.data, k)
        return l, r, k if r>l else (self.data[l-1] if l>0 else None)
        
class MasterNode:
    def __init__ (self, data_nodes):
        assert (len(data_nodes) >= 1)
        self.data_nodes = data_nodes
        self.size = 0

        left, right, _ = self.data_nodes[0].get_range ()
        for node in self.data_nodes:
            l, r, s = node.get_range()
            if l < left : left  = l
            if r > right: right = r
            self.size += s

        self.range = (left, right)

    def get_nth_element (self, k):
        assert (k > 0 and k <= self.size)
        loop_times = 0

        lo, hi = self.range
        while True:
            loop_times += 1
            mid = lo + (hi - lo) / 2
            
            left, right, val = 0, 0, None
            for node in self.data_nodes:
                l, r, v = node.query_bound (mid)
                left  += l
                right += r
                val = max (v, val)

            if k > left and k <=right:
                print 'loop_times =', loop_times
                return val

            if k <= left:
                hi = mid
            else:
                lo = mid + 1

for i in xrange(100):
    data   = random.randint(0, 500, 1000)
    slaves = [SlaveNode(data[10*i:10*(i+1)]) for i in range(100)]
    master = MasterNode(slaves)

    idx    = random.randint(1,1001)
    ret    = master.get_nth_element(idx)
    assert (ret == sorted(data)[idx-1])
