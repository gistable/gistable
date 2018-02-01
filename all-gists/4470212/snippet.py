import inspect
from pickle import loads, dumps
from IPython.utils import pickleutil


def class_dumps(cls):
    canned_dict = pickleutil.canDict(
        dict((k, v) for k, v in cls.__dict__.items()
             if k not in ('__weakref__', '__dict__')))
    parents = tuple(cls.mro())
    # TODO: recursively call class_dumps on parents that can from the same
    # module as the module of cls
    return dumps((cls.__name__, parents, canned_dict))


def class_loads(cls_str):
    name, parents, canned_dict  = loads(cls_str)
    return type(name, parents, pickleutil.uncanDict(canned_dict))


# Let's define some classes to copy and %paste into an interactive ipython
# session:
"""

class AClass(object):

    def __init__(self, a):
        self.a = a

    def a_method(self, b):
        return self.a + b


class BClass(AClass):

    def b_method(self, b):
        return self.a_method(b) * 2


AClassClone = class_loads(class_dumps(AClass))
BClassClone = class_loads(class_dumps(BClass))
b = BClassClone(3)
b.b_method(4)

"""
