from __future__ import print_function
from collections import OrderedDict
from numbers import Number
import collections
import sys


PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,
else:
    string_types = basestring,


def der(obj):
    """Prints a human-readable of the attributes of any python objects

   <class '__main__.Mock'>
              mydict : dict                 	 indexable, iterable, mapping
             myfloat : float                	 number
              myfunc : instancemethod       	 callable
               myint : int                  	 number
              myiter : generator            	 iterable
            mylambda : instancemethod       	 callable
              mylist : list                 	 indexable, iterable
            myscalar : int                  	 number
            mystring : str                  	 indexable, iterable, string
    """
    data = OrderedDict()
    for propname in dir(obj):
        if propname.startswith('_'):
            continue
        data[propname] = list()

        prop = getattr(obj, propname)

        if hasattr(prop, '__call__'):
            data[propname].append('callable')

        if isinstance(prop, collections.Iterable) or \
           hasattr(prop, '__iter__'):
            data[propname].append('iterable')

        if isinstance(prop, collections.Mapping) or \
           hasattr(prop, '__getattr__'):
            data[propname].append('mapping')

        if hasattr(prop, '__getitem__'):
            data[propname].append('indexable')

        if isinstance(prop, Number):
            data[propname].append('number')

        if isinstance(prop, string_types):
            data[propname].append('string')

    print(type(obj))
    for k, v in data.items():
        typ = type(getattr(obj, k)).__name__
        print('{0: >20} : {1: <20} \t {2}'.format(k, typ, ', '.join(sorted(v))))


def __test__():
    def testiter():
        for i in range(10):
            yield i**2

    import numpy as np

    class Mock(object):
        myint = 1
        myfloat = float('nan')
        mystring = "i'm a string"
        mylist = ['I', 'am', 'a', 'list']
        myfunc = testiter
        mylambda = lambda x: x + 1
        myiter = testiter()
        myscalar = np.asscalar(np.array([24]))
        mydict = {'a': 123}
        # bytes

    der(Mock())


if __name__ == '__main__':
    __test__()