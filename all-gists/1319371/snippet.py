from collections import namedtuple
def convert(dictionary):
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)

"""
>>> d = dictionary(a=1, b='b', c=[3])
>>> named = convert(d)
>>> named.a == d.a
True
>>> named.b == d.b
True
>>> named.c == d.c
True
"""