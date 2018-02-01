class LazyDict:
    '''Use a 2-tuple generator as a lazily-evaluated dictionary.'''
    def __init__(self, gen):
        self.gen = gen
        self.dict = {}

    def _generate_to(self, key):
        while key not in self.dict:
            found_key, found_val = next(self.gen)
            self.dict[found_key] = found_val
        return True

    def __contains__(self, key):
        try:
            return self._generate_to(key)
        except StopIteration:
            return False

    def __getitem__(self, key):
        if key in self:
            return self.dict[key]
        else:
            raise KeyError

    def __iter__(self):
        yield from self.dict
        for found_key, found_val in self.gen:
            self.dict[found_key] = found_val
            yield found_key

    def get(self, key, default=None):
        return self[key] if key in self else default

    def items(self):
        return ((key, self[key]) for key in self)

    def keys(self):
        yield from self

    def values(self):
        return (self[key] for key in self)


def dgen(x):
    i = 0
    while True:
        yield i, x ** i
        i += 1

d = LazyDict(dgen(2))
print(d[5])
print(d[10])
print(22 in d)


bar = LazyDict((i, i**2) for i in range(20))
print(bar[3])
print(bar.get(42, 'unknown'))

for k in bar.keys():
    print(k, bar[k])

print(-4 in bar)
