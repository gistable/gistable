from collections import Iterable

def flatten(items):
    for item in items:
        if isinstance(item, Iterable):
            yield from flatten(item)
        else:
            yield item

nested = [1, 3, [3, [4, 5, [6]]]]
print(list(flatten(nested)))

[1, 3, 3, 4, 5, 6]