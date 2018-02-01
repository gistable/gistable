"""
These two repr implementations make a "repr" that you can just drop into your class if it's a simple one.
"""

class A:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return "%s(**%r)" % (self.__class__.__name__, self.__dict__)

print A(1,3)
# A(**{'y': 3, 'x': 1})

class B:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        ctor_str = ', '.join('%s=%r' % pair for pair in (self.__dict__.items()))
        return "%s(%s)" % (self.__class__.__name__, ctor_str)

print B(1,3)
# B(y=3, x=1)

