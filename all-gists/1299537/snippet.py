def ichunk(s, size):
    return (s[i: i+size] for i in xrange(0, len(s), size))

def ichain(iterable):
"""Better than itertools.chain because it does not use *args"""
    for inner in iterable:
        for item in inner:
            yield item