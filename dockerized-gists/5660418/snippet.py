__author__ = 'robert'

"""
Implementation inspired by Petr Mitrichev's blog post http://petr-mitrichev.blogspot.co.nz/2013/05/fenwick-tree-range-updates.html
and
Yoshiya Miyata's Quora answer http://qr.ae/pHhNN
"""

class Bit:
    def __init__(self, n):
        sz = 1
        while n >= sz:
            sz *= 2
        self.size = sz
        self.data = [0]*sz

    def sum(self, i):
        assert i > 0
        s = 0
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def add(self, i, x):
        assert i > 0
        while i < self.size:
            self.data[i] += x
            i += i & -i

from random import randint

query_tests = 1
for n in range(1,18):
    bit = Bit(n)
    tracker = [0]*n
    for _ in range(3000):
        index_to_update = randint(0, n-1)
        value = randint(0, 50)
        tracker[index_to_update] += value
        #print "adding value %s to index %s" % (value, index_to_update)
        bit.add(index_to_update+1, value)
        for i in range(n):
            #print "querying index %s" % i
            sum1 = sum(tracker[:i+1])
            sum2 = bit.sum(i+1)
            #print n, i, sum1, sum2, tracker, bit.data, tracker[:i+1]
            assert sum1 == sum2
            query_tests += 1

print "passed %s tests" % query_tests

class RangeBit:
    def __init__(self, n):
        sz = 1
        while n >= sz:
            sz *= 2
        self.size = sz
        self.dataAdd = [0]*sz
        self.dataMul = [0]*sz

    def sum(self, i):
        assert i > 0
        add = 0
        mul = 0
        start = i
        while i > 0:
            add += self.dataAdd[i]
            mul += self.dataMul[i]
            i -= i & -i
        return mul * start + add

    def add(self, left, right, by):
        assert 0 < left <= right
        self._add(left, by, -by * (left - 1))
        self._add(right, -by, by * right)

    def _add(self, i, mul, add):
        assert i > 0
        while i < self.size:
            self.dataAdd[i] += add
            self.dataMul[i] += mul
            i += i & -i

range_tests = 1
for n in range(1,18):
    bit = RangeBit(n)
    tracker = [0]*n
    for _ in range(3000):
        index_to_update = randint(0, n-1)
        index_to_update2 = randint(0, n-1)
        value = randint(0, 50)
        left = min(index_to_update, index_to_update2)
        right = max(index_to_update, index_to_update2)
        #print "adding value %s to index pair left %s right %s" % (value, left, right)
        tracker[left:right+1] = [v + value for v in tracker[left:right+1]]
        bit.add(left + 1, right + 1, value)
        for i in range(n):
            #print "querying index %s" % i
            sum1 = sum(tracker[:i+1])
            sum2 = bit.sum(i+1)
            assert sum1 == sum2
            range_tests += 1
print "ran %s range tests" % range_tests