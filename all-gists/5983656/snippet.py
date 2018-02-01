import random
class _:
    def __init__(self, data):
        if isinstance (data, _): return data
        self.data = data

    def value (self):
        return self.datan

    def each (self, func):
        return [func(i) for i in self.data]

    def map (self, func):
        return _(map(func, self.data))

    def reduce (self, func, init = None):
        return _(reduce (func, self.data, init))

    def reduce_right (self, func, init = None):
        pass

    def filter (self, func=bool):
        return _([i for i in self.data if func(i)])

    def find (self, func):
        for i in self.data:
            if func(i): return i

    def where (self): pass

    def find_where (self): pass

    def reject (self, func=bool):
        return self.filter (lambda x: not func(x))

    def every (self, func=bool):
        all(map(func, self.data))

    def some (self, func=bool):
        for i in self.data:
            if func(i): return True

    def contains (self, item):
        return item in self.data

    def invoke (self): pass

    def pluck (self): pass

    def max (self, func):
        return max(map(func), data)

    def min (self, func):
        return max(map(func), data)

    def sort_by (self, func):
        return _(sorted (self.data, cmp=func))

    def group_by (self, func):
        result = {}
        for i in self.data:
            key = func(i)
            if result.has_key(key) : result[key].append(i)
            else : result[key] = [i]
        return _(result)

    def shuffle (self):
        return _(random.shuffle(self.data))

    def size (self):
        return len(self.data)

    def to_list (self):
        if isinstance(self.data, 'dict') : return self.data.items()
        return list(self.data)

# -------------------------- list only --------------------------

    def first (self):
        return self.data[0]

    def but_last (self, n):
        return _(self.data[0:-n])

    def initial (self, n):
        return self.data.but_last(n)

    def rest (self, n):
        return _(self.data[n:])

    def compact (self, n):
        return self.filter()

    def flatten (self): pass

    def without (self, *args):
        return self.reject(lambda x: x in args)

    def union (self) : pass





a = _(range(1, 10))
t = (a.map(lambda x: x+ 1)
     .filter(lambda y: y > 2)
     .reject(lambda x: x < 5)
     .sort_by(lambda x, y : y - x)
     .without(3, 9))
print t.data

print _([1,2,3]).some()