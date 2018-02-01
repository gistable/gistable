import random
import math
class Num(object):
    def __init__(self, val):
        self.value = val
        self.bit = False
    def __repr__(self):
        return str(self.value)
    def __abs__(self):
        return self
    def __floor__(self):
        return Num(math.floor(self.value))
    def __ceil__(self):
        return Num(math.ceil(self.value))
    def __trunc__(self):
        return Num(math.trunc(self.value))
    def __round__(self):
        return Num(round(self.value))
    def __pos__(self):
        if self.bit:
            self.value += 1
            self.bit = False
        else:
            self.bit = True
        return self
    def __neg__(self):
        if self.bit:
            self.value -= 1
            self.bit = False
        else:
            self.bit = True
        return self
    def __add__(self, other):
        return Num(self.value + other)
    def __radd__(self, other):
        return Num(self.value + other)
    def __iadd__(self, other):
        self.value += other
        return self
    def __sub__(self, other):
        return Num(self.value - other)
    def __rsub__(self, other):
        return Num(other - self.value)
    def __isub__(self, other):
        self.value -= other
        return self
    def __mul__(self, other):
        return Num(self.value * other)
    def __rmul__(self, other):
        return Num(self.value * other)
    def __imul__(self, other):
        self.value *= other
        return self
    def __mod__(self, other):
        return Num(self.value % other)
    def __rmod__(self, other):
        return Num(self.value % other)
    def __imod__(self, other):
        self.value %= other
        return self
    def __pow__(self, other):
        return Num(self.value ** other)
    def __rpow__(self, other):
        return Num(self.value ** other)
    def __ipow__(self, other):
        self.value **= other
        return self
    def __floordiv__(self, other):
        return Num(self.value // other)
    def __rfloordiv__(self, other):
        return Num(other // self.value)
    def __ifloordiv__(self, other):
        self.value //= other
        return self
    def __truediv__(self, other):
        return Num(self.value / other)
    def __rtruediv__(self, other):
        return Num(other / self.value)
    def __itruediv__(self, other):
        self.value /= other
        return self
    def __invert__(self):
        return Num(self.value + random.random()-0.5)
