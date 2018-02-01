"""
Results:

multiple_update: 57 ms
copy_and_update: 46 ms
dict_constructor: 56 ms
kwargs_hack: 45 ms
dict_comprehension: 45 ms
concatenate_items: 166 ms
union_items: 163 ms
chain_items: 122 ms
chainmap: 86 ms
dict_from_chainmap: 445 ms
dict_unpacking: 27 ms

"""
import timeit


setup = """
from collections import ChainMap
from itertools import chain

def multiple_update(dict_a, dict_b):
    merged = {}
    merged.update(dict_a)
    merged.update(dict_b)
    return merged


def copy_and_update(dict_a, dict_b):
    merged = dict_a.copy()
    merged.update(dict_b)
    return merged


def dict_constructor(dict_a, dict_b):
    merged = dict(dict_a)
    merged.update(dict_b)
    return merged


def kwargs_hack(dict_a, dict_b):
    return dict(dict_a, **dict_b)


def dict_comprehension(dict_a, dict_b):
    return dict(dict_a, **dict_b)


def concatenate_items(dict_a, dict_b):
    return dict(list(dict_a.items()) + list(dict_b.items()))


def union_items(dict_a, dict_b):
    return dict(list(dict_a.items()) + list(dict_b.items()))


def chain_items(dict_a, dict_b):
    return dict(chain(dict_a.items(), dict_b.items()))


def chainmap(dict_a, dict_b):
    return ChainMap({}, dict_b, dict_a)


def dict_from_chainmap(dict_a, dict_b):
    return dict(ChainMap(dict_b, dict_a))


def dict_unpacking(dict_a, dict_b):
    return {**dict_a, **dict_b}


defaults = {'name': "Anonymous User", 'page_name': "Profile Page"}
user = {'name': "Trey", 'website': "http://treyhunner.com"}
"""


def time_function(func_name):
    timed_code = "context = {}(defaults, user)".format(func_name).strip()
    time = min(timeit.Timer(timed_code, setup=setup).repeat(7, 100000))
    print("{}: {} ms".format(func_name, int(time * 1000)))


time_function("multiple_update")
time_function("copy_and_update")
time_function("dict_constructor")
time_function("kwargs_hack")
time_function("dict_comprehension")
time_function("concatenate_items")
time_function("union_items")
time_function("chain_items")
time_function("chainmap")
time_function("dict_from_chainmap")
time_function("dict_unpacking")