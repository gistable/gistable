import collections


class OrderedDefaultDict(collections.OrderedDict, collections.defaultdict):
    pass


odd = OrderedDefaultDict()
odd.default_factory = list

odd['a'].append(True)
odd['b'].append(False)
odd['c'].append(False)

print(odd.items())
print(odd['d'])