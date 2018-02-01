from __future__ import with_statement
from types import ClassType, MethodType, TypeType


class Patch(object):

    class Missing:
        pass

    def __init__(self, obj, **kwargs):
        self._obj = obj
        self._patches = kwargs

    def __enter__(self):
        self._saved = {}
        for name, method in self._patches.iteritems():
            self._saved[name] = self._obj.__dict__.get(name, self.Missing)
            setattr(self._obj, name, self._rebind_method(method))

    def __exit__(self, exc_type, exc_value, traceback):
        for name, method in self._saved.iteritems():
            if method is not self.Missing:
                setattr(self._obj, name, method)
            else:
                delattr(self._obj, name)

    def _rebind_method(self, method):
        if not method:
            method = self._get_noop_method()
        if isinstance(method, MethodType):
            method = self._get_unbound_method(method)
        if not isinstance(self._obj, (ClassType, TypeType)):
            method = self._bind_method_to_instance(method)
        return method

    def _get_noop_method(self):
        return lambda *args, **kwargs: None

    def _get_unbound_method(self, method):
        return method.im_func

    def _bind_method_to_instance(self, method):
        return method.__get__(self._obj, type(self._obj))