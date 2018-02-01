#!/usr/bin/env python

# requires python >= 2.7
# see: https://pypi.python.org/pypi/ordereddict
from collections import OrderedDict

MAXLRU = 200

class LRU(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size = kwds.pop("size", MAXLRU)
        OrderedDict.__init__(self, *args, **kwds)
        self.limit()
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)
        self.limit()
    def limit(self):
        while len(self) > self.size:
            self.popitem(last=False)