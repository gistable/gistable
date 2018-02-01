#!/usr/bin/env python

"""A dict-like object that supports JS object syntax.

AttrDict is a dict that can be called using either square brackets, like a
normal dict, or by using attributes--just like in JavaScript.

Accessing the value for an undefined key will return None (Python's equivalent
to undefined).

Just a toy. Don't use in production. ;)
--Kirsle"""

class AttrDict(object):
    def __init__(self, **kwargs):
        self.__dict__.update(dict(**kwargs))

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, name):
        return self.get(name)

    def get(self, name, default=None):
        return self.__dict__.get(name, default)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __setitem__(self, name, value):
        self.__dict__[name] = value

    def __delattr__(self, name):
        del self.__dict__[name]

    def __delitem__(self, name):
        del self.__dict__[name]

    def __str__(self):
        return str(dict(self.__dict__))

    def __repr__(self):
        return "AttrDict({})".format(repr(self.__dict__))


test = AttrDict(hello="world")
print test.hello
test.goodbye = "mars"
print test.goodbye

print test["hello"]

print test
print repr(test)

del test["hello"]
del test.goodbye

test["abc"] = "123"
print test.get("abc")
print test.get("badkey", "default")

test.hello = AttrDict()
test.hello.world = AttrDict()
test.hello.world.key = "value"
print test.hello.world.key
print test["hello"].world["key"]
print test["hello"]["world"].key

print repr(test)

# Bad keys return None
print test.badkey
print test["badkey"]