import operator
from collections import namedtuple

class Heap(object):
    def __init__(self, from_iterable=None, kind='min'):
        operators_type = namedtuple('Operators', 'lt, lte, gt, gte')
        
        kinds = {
            'min': operators_type(
                        operator.lt,
                        operator.le,
                        operator.gt,
                        operator.ge),
                        
            'max': operators_type(
                        operator.gt,
                        operator.ge,
                        operator.lt,
                        operator.le),
        }
        
        if kind not in kinds:
            raise ValueError('No such kind "%s"' % (kind))
    
        self.operators = kinds[kind]
        self.heap = [None]
        
        if hasattr(from_iterable, '__iter__'):
            for item in from_iterable:
                self.insert(item)

    def __iter__(self):
        while True:
            item = self.pop_head()
            if item is None:
                raise StopIteration()
            yield item

    def __len__(self):
        return len(self.heap) - 1

    def empty(self):
        return len(self.heap) - 1 == 0

    @staticmethod
    def swap(_list, a, b):
        tmp = _list[a]
        _list[a] = _list[b]
        _list[b] = tmp

    def insert(self, value):
        if value is None:
            raise TypeError('"value" cannot be of NoneType')
    
        self.heap.append(value)
        self.bubble_up(len(self.heap) - 1)

    def bubble_up(self, i):
        lt, lte, gt, gte = self.operators
        
        while i > 1:
            h = i // 2
            if lt(self.heap[i], self.heap[h]):
                self.swap(self.heap, i, h)

            i = h

    def percolate_down(self, i):
        lt, lte, gt, gte = self.operators
    
        while (i * 2) < len(self.heap):
            d = i * 2
            if (d + 1 < len(self.heap) and gte(self.heap[d], self.heap[d + 1])):
                d += 1
            
            if gt(self.heap[i], self.heap[d]):
                self.swap(self.heap, i, d)
    
            i = d

    def head(self):
        if len(self.heap) == 1:
            return None
    
        return self.heap[1]

    def pop_head(self):
        if len(self.heap) == 1:
            return None

        item = self.heap[1]
        last = self.heap.pop(-1)
        
        if len(self.heap) > 1:
            self.heap[1] = last
            self.percolate_down(1)

        return item

    def bfs(self):
        for i in self.heap[1:]:
            yield i

if __name__ == '__main__':
    import sys, random
    
    values = [random.randint(0, 100) for i in range(16)]
    values_sorted = sorted(values)
    
    heap = Heap(values, kind='min')
    i = 0
    for item in heap:
        assert item == values_sorted[i]
        i += 1
    
    sys.exit(0)
