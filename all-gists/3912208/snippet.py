import random
import types


# Two ways to create "bound" methods from plain functions
def bind(instance, f):
    """Bind function f to the given instance."""
    return lambda *args, **kwargs: f(instance, *args, **kwargs)

def make_method(instance, f):
    """Create an actual method object for function f bound to the given
    instance.

    Source: http://countergram.com/adding-bound-methods
    """
    return types.MethodType(f, instance, instance.__class__)


# We'll use both of those binding functions when creating instances of this
# class.
class Foo(object):
    def __init__(self, x, mutators):
        mutator = random.choice(mutators)
        print 'Using mutator %s' % mutator.__name__
        self.bar = bind(self, mutator)
        self.baz = make_method(self, mutator)
        self.x = x


# The methods from which we'll be choosing at instantiation time.
def identity(self):
    return self.x

def double(self):
    self.x *= 2
    return self.x

def halve(self):
    self.x /= 2
    return self.x

def square(self):
    self.x = self.x ** 2
    return self.x

mutators = [
    identity,
    double,
    halve,
    square,
]


# Make an instance and try out our "bound" methods
foo = Foo(10, mutators)
print foo.bar()
print foo.baz()
