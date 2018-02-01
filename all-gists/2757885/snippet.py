#!/usr/bin/python
import inspect
from functools import wraps
from collections import defaultdict

# This time, we'll avoid using a class to hold the namespace. We'll just use
# the class that the functions are being defined in.

# AS A BONUS
# This means that it works for module-level functions, not just methods!

def get_class_cache():
    # Assuming that we are in a second function call from the class itself
    # class def -> guard -> get_class_cache
    class_ns = inspect.stack()[2][0].f_locals
    if '__guards' not in class_ns:
        class_ns['__guards'] = {}
        class_ns['__guard_implementations'] = defaultdict(list)
    return (class_ns['__guards'], class_ns['__guard_implementations'])

def get_guard_function(f, guards, implementations):
    name = f.func_name
    if name not in guards:
        @wraps(f)
        def wrap(*args, **kwargs):
            for impl in implementations[name]:
                try:
                    return impl(*args, **kwargs)
                except TypeError:
                    continue
            else:
                raise TypeError("%s doesn't have a function matching %d args and %r kwargs" % (name, len(args), kwargs.keys()))
        guards[name] = wrap
    return guards[name]

def guard(f):
    guards, implementations = get_class_cache()
    implementations[f.func_name].append(f)
    return get_guard_function(f, guards, implementations)


class T(object):
    # Because this doesn't need an argument,
    # it'll be used instead of foo(self) below if you uncomment it
#    @guard
#    def foo(self, bar="<default>"):
#        print bar, "foo!"

    @guard
    def foo(self):
        print "foo!"

    @guard
    def foo(self, bar="<default>"):
        print bar, "foo!"

t = T()

t.foo()
t.foo('baz')
# This will throw an exception
t.foo('quux', 'baz')


# That module-level magic:

@guard
def quux():
    print "quux"

@guard
def quux(name):
    print "quux,", name

quux()
quux('xuuq')