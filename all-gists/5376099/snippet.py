'''
Implements a ORM-like interface to Redis
http://synack.me/blog/hack-1-a-simple-orm-for-python-and-redis
'''

import inspect
import redis
import json
import sys

def objectify(keys):
    '''
    Transform a list of keys into a list of object instances
    '''
    # Get all the model types in this module
    types = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))

    # Split the keys into typename, name
    keys = [x.split(':', 1) for x in keys]

    # Lookup and instantiate each object
    objects = [types[typename](name) for typename, name in keys]
    return objects


class Model(object):
    db = redis.Redis()

    def __init__(self, name):
        self.name = name
        self.key = '%s:%s' % (self.__class__.__name__, name)

    def add_reference(self, obj):
        self.db.sadd('%s:refs' % self.key, obj.key)

    def delete_reference(self, obj):
        self.db.srem('%s:refs' % self.key, obj.key)

    def references(self):
        return objectify(self.db.smembers('%s:refs' % self.key))

    def delete(self):
        self.db.delete(self.key)

        keys = self.db.smembers('%s:refs' % self.key)
        refs = objectify(keys)
        for obj in refs:
            if hasattr(obj, 'dereference'):
                obj.dereference(self)

    def __str__(self):
        return self.key

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.name)


class SetModel(Model):
    def __init__(self, name):
        Model.__init__(self, name)
        self.setkey = self.key + ':set'

    def add(self, obj):
        self.db.sadd(self.setkey, obj.key)
        obj.add_reference(self)

    def remove(self, obj):
        self.db.srem(self.setkey, obj.key)
        obj.delete_reference(self)

    def dereference(self, obj):
        self.remove(obj)

    def __len__(self):
        return self.db.scard(self.setkey)

    def __iter__(self):
        return objectify(self.db.smembers(self.setkey)).__iter__()

    @classmethod
    def intersect(cls, sets):
        return objectify(cls.db.sinter([x.setkey for x in sets]))


class DictModel(Model):
    def __init__(self, name):
        Model.__init__(self, name)
        self.dictkey = self.key + ':dict'

    def __setitem__(self, key, value):
        self.db.hset(self.dictkey, key, json.dumps(value))

    def __delitem__(self, key):
        self.db.hdel(self.dictkey, key)

    def __getitem__(self, key):
        value = self.db.hget(self.dictkey, key)
        if value is None:
            raise KeyError('Key "%s" does not exist in %s' % (key, self.dictkey))
        else:
            return json.loads(value)

    def keys(self):
        return self.db.hkeys(self.dictkey, key)

    def __len__(self):
        return self.db.hlen(self.dictkey)

    def items(self):
        items = self.db.hgetall(self.dictkey).items()
        items = [(k, json.loads(v)) for k, v in items]
        return items


class Server(DictModel):
    pass


class Tag(DictModel, SetModel):
    def __init__(self, name):
        DictModel.__init__(self, name)
        SetModel.__init__(self, name)