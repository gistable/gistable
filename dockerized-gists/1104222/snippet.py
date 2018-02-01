# Python 2.5 compatibility hack for property.setter, property.deleter
import __builtin__
if not hasattr(__builtin__.property, "setter"):
    class property(__builtin__.property):
        __metaclass__ = type
        
        def setter(self, method):
            return property(self.fget, method, self.fdel)
            
        def deleter(self, method):
            return property(self.fget, self.fset, method)
            
        @__builtin__.property
        def __doc__(self):
            """Doc seems not to be set correctly when subclassing"""
            return self.fget.__doc__
