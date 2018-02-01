# -*- coding: utf-8 -*-
import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle


class PythonObjectCache(object):
    @classmethod
    def to_python(cls, value):
        return pickle.loads(str(value))

    @classmethod
    def serialize(cls, obj):
        return pickle.dumps(obj)

    @classmethod
    def set(cls, key, obj, timeout=0):
        from django.core.cache import cache
        serialized = cls.serialize(obj)
        cache.set(key, serialized, timeout)

    @classmethod
    def get(cls, key, default=None):
        from django.core.cache import cache
        value = cache.get(key, default)
        if value:
            return cls.to_python(value)
        return default