#!/usr/bin/env python

import json
from collections import OrderedDict

def make_repr(*fields):
    def repr(self):
        return json.dumps(OrderedDict((f, getattr(self, f)) for f in fields),
                          indent=4)
    return repr


class Point:
    __repr__ = make_repr('x', 'y')
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


p = Point(1,2,3)
print(repr(p))



