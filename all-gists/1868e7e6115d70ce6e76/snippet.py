import sys
import warnings
from types import ModuleType
from importlib import import_module

try:
    basestring
except NameError:
    basestring = str

class FancyModule(object):
    
    __class__ = ModuleType
    
    def __init__(self, original):
        self.__dict__ = original.__dict__
        self.__auto_import__ = set()
        self.__warn_on_access__ = {}
        self.__name__ = original.__name__

    def __getattr__(self, name):
        if name in self.__auto_import__:
            assert "." not in name
            # FIXME: this next line requires 2.7+.
            mod = import_module("." + name, package=self.__package__)
            # import has probably done this implicitly, but let's be explicit:
            setattr(self, name, mod)
            return mod

        if name in self.__warn_on_access__:
            value, warning = self.__warn_on_access__[name]
            warnings.warn(warning, stacklevel=2)
            return value

        raise AttributeError(name)

    def __dir__(self):
        result = set(self.__dict__)
        result.update(self.__auto_import__)
        result.update(self.__warn_on_access__)
        return sorted(result)

    def __repr__(self):
        return "<module %s>" % self.__name__

def install(name, class_=FancyModule):
    orig_module = sys.modules[name]
    if isinstance(orig_module, class_):
        return
    new_module = FancyModule(orig_module)
    sys.modules[name] = new_module
