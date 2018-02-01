import itertools
import collections

def flattened(x):
    if isinstance(x, collections.Iterable):
        for y in x:
            for z in flattened(y):
                yield z
    else:
        yield x

# Uses python 3.3s generator delegation (PEP-380)
def flattened(x):
    if isinstance(x, collections.Iterable):
        for y in x:
            yield from flattened(y)
    else:
        yield x

def flattened(x):
    if isinstance(x, collections.Iterable):
        x = iter(x)
	while True:
            try:
                head = x.next()
            except StopIteration:
                break
            if isinstance(head, collections.Iterable):
                x = itertools.chain(head, x)
            else:
                yield head
    else:
    	yield x

print list(flattened(0))
print list(flattened([0]))
print list(flattened((x for x in range(4))))
print list(flattened([0, 1, 2]))
print list(flattened([0, [1], 2]))
print list(flattened([0, [1, 2, 3, [4, 5]], [2], (3, 4, 2)]))
print list(flattened([0, [1, 2, 3, [4, 5]], [2], (3, 4, 2), (x for x in range(4))]))
