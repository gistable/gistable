# THIS VERSION IS OUTDATED 
# see .inplace(), .cloning(), ._clone() and .clone() methods of QuerySetMixin
# in https://github.com/Suor/django-cacheops/blob/master/cacheops/query.py
from django.conf import settings
from django.db.models import Model, Manager

MUTATING_QUERYSETS = getattr(settings, 'MUTATING_QUERYSETS', False)

class QuerySetMixin(object):
    def __init__(self, *args, **kwargs):
        self._no_monkey.__init__(self, *args, **kwargs)
        self._inplace = MUTATING_QUERYSETS

    def inplace(self):
        self._inplace = True
        return self

    def _clone(self, klass=None, setup=False, **kwargs):
        if self._inplace and klass is None:
            self.__dict__.update(kwargs)
            return self
        else:
            return self._no_monkey._clone(self, klass, setup, **kwargs)

class ManagerMixin(object):
    def inplace(self):
        return self.get_query_set().inplace()


from inspect import getmembers, ismethod

class MonkeyProxy(object):
    def __init__(self, cls):
        monkey_bases = tuple(b._no_monkey for b in cls.__bases__ if hasattr(b, '_no_monkey'))
        for monkey_base in monkey_bases:
            for name, value in monkey_base.__dict__.iteritems():
                setattr(self, name, value)

def monkey_mix(cls, mixin, methods=None):
    """
    Mixs in a class to other existing class using monkey patches.
    Mixin method can call overwritten ones using special proxy object stored in _no_monkey attribute.
    class SomeMixin(object):
        def do_smth(self, arg):
            ... do smth else before
            self._no_monkey.do_smth(self, arg)
            ... do smth else after
    """
    assert '_no_monkey' not in cls.__dict__, 'Multiple monkey mix not supported'
    cls._no_monkey = MonkeyProxy(cls)

    if methods is None:
        methods = getmembers(mixin, ismethod)
    else:
        methods = [(m, getattr(mixin, m)) for m in methods]

    for name, method in methods:
        if hasattr(cls, name):
            setattr(cls._no_monkey, name, getattr(cls, name))
        setattr(cls, name, method.im_func)


monkey_mix(Manager, ManagerMixin)
monkey_mix(QuerySet, QuerySetMixin)