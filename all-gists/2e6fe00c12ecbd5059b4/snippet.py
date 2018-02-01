class Property(object):

    def __init__(self, name):
        self.__name__ = '__%s' % name

    def __get__(self, obj, cls=None):
        return obj.__dict__[self.__name__]

    def __set__(self, obj, val):
        obj.__dict__['__%s' % self.__name__] = val

    def __delete__(self, obj):
        del obj.__dict__[self.__name__]


class AutoProperty(object):

    def _auto_property(self, l, property_descriptor):
        print("auto prop init")
        del(l['self'])
        for k in l:
            self.__dict__[k] = property_descriptor(k)
            self.__dict__[k] = l[k]
            
            
class City(AutoProperty):

    # properties
    name = None
    county_code = None

    def __init__(self,
                 name: str=None,
                 county_code: str=None):
        self._auto_property(locals(), Property)
