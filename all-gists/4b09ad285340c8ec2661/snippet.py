# maybe.py - a Pythonic implementation of the Maybe monad
# Copyright (C) 2014. Senko Rasic <senko.rasic@goodcode.io>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


__all__ = ['Maybe', 'Just', 'Nothing', 'lift']


def lift(fn):
    """lift a function to Maybe monad

    Converts a plain function to one that can accept Maybe arguments
    (positional or keyword) and returns a Maybe return value.

    The returning function returns Nothing if any of the arguments is Nothing.
    Otherwise, it returns Just(<return value of the original function>).

    The converted function accepts both Maybe (which are unpacked) and
    non-Maybe arguments (which are used as-is).

    Examples:

    >>> maybe_abs = lift(abs)
    >>> maybe_abs(Just(-1))
    Just(1)
    >>> maybe_abs(Nothing)
    Nothing
    >>> maybe_abs(0)
    Just(0)

    """

    def wrapper(*args, **kwargs):
        def lift_arg(arg):
            return arg.value if isinstance(arg, Maybe) else arg

        largs = []
        for arg in args:
            if arg is Nothing:
                return Nothing
            else:
                largs.append(lift_arg(arg))
        lkwargs = {}
        for k, v in kwargs.items():
            if v is Nothing:
                return Nothing
            else:
                lkwargs.append(lift_arg(arg))
        return Maybe(fn(*largs, **lkwargs))
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


class Maybe(object):
    """Maybe monad

    Wraps a value (or nonexistence of the value) inside an opaque container.
    The container can be used in place of the actual value in all operations
    (including mathematical and logical operations, attribute access and
    function calls).

    The monad is either `Nothing` (a singleton object like None, signalling
    the nonexistence of any value) or `Just(value)` (a wrapper around the
    actual value).

    All operations on the monad are short-circuited to return `Nothing` if
    the monad is `Nothing`, and to perform the operation on the actual value
    if the monad is `Just(value)`. This allows for easy chaining of operations
    on a value without checking for result existence or validity after each
    step.

    Nothing is a singleton and different from any Just value:

    >>> Nothing is (Nothing + Nothing)
    True
    >>> Nothing is Just(None)
    False

    Math/logical operators work as expected:

    >>> assert (Nothing == 1) is Nothing
    >>> assert Nothing + Just(1) is Nothing
    >>> assert Nothing - 1 is Nothing
    >>> assert 2 * Nothing is Nothing
    >>> assert Just(2) / Nothing is Nothing
    >>> assert Just(10) % 3 == Just(1)
    >>> assert Just(5) > 3
    >>> assert Just(5) == 5
    >>> assert Just(5) < 6
    >>> assert Just(5) != 6

    Note that Nothing in boolean context is always False (for easier checking
    without explicit cast to `bool`), while Just is False or True depending
    on its value:

    >>> bool(Nothing)
    False
    >>> bool(1)
    True
    >>> bool(0)
    False

    Accessing attributes on Maybe either short-cuts to Nothing or accesses
    the corresponding attributes in the contained value:

    >>> assert Nothing.foo is Nothing
    >>> assert Just('hello').upper() >> str == 'HELLO'

    Maybe is a callable and will either short-circuit for Nothing, or call
    the contained value:

    >>> assert Nothing() is Nothing
    >>> assert Just(lambda: 42)() >> int == 42

    The above two facts, combined, mean that we can do something like:

    >>> Just("hello world").upper()
    Just('HELLO WORLD')

    Right-shift operator (>>) can be used in the same way as monadic bind
    in Haskell (>>=):

    >>> Just(5) >> (lambda x: Just(x * 2))
    Just(10)

    In Python, this is useful for getting the value back from the Monad, and
    at the same time verifying that it can be cast to a specific type:

    >>> Just(5) >> int
    5
    >>> Just('hello') >> int
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 10: 'hello'

    Often it is useful to get either the actual value (if any) or a default
    value in case of Nothing. Although this can be done with >>, there's a
    nicer and shorter syntax for it using the bitwise or operator (|):

    >>> Just(5) | 0
    5
    >>> Nothing | 0
    0

    When cast to string or unicode, Nothing will evaluate to an empty string,
    and Just will just call the to-string conversion methods of the contained
    value.

    >>> str(Nothing)
    ''
    >>> unicode(Nothing)
    u''

    And finally, here's proof `Maybe` really is a monad (required axioms hold):

    >>> assert (Just(42) >> int) == 42  # (return x) >>= f <=> f x
    >>> assert (Just('hello') >> str) == 'hello'  # (return x) >>= f <=> f x
    >>> assert (Just(42) >> Just) == Just(42)  # m >>= return <=> m
    >>> assert (Just('hello') >> Just) == Just('hello')  # m >>= return <=> m
    >>> # (m >>= f) >>= g <=> m >>= (lambda x -> (f x >>= g))
    >>> assert ((Just(-1) >> (lambda x: Just(abs(x))) >> str) ==
    ... Just(-1) >> (lambda x: str(abs(x))) == '1')

    """
    class __metaclass__(type):

        ops = ['add', 'sub', 'mul', 'div', 'mod', 'eq', 'ne', 'lt', 'gt']

        def __new__(mcs, name, bases, dct):
            import operator

            def reverse(fn):
                wrapper = lambda x, y: fn(y, x)
                wrapper.__name__ = fn.__name__
                wrapper.__doc__ = fn.__doc__
                return wrapper

            for opname in mcs.ops:
                op = getattr(operator, opname)
                dct['__' + opname + '__'] = lift(op)
                dct['__r' + opname + '__'] = lift(reverse(op))

            return type.__new__(mcs, name, bases, dct)


    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Nothing' if self is Nothing else 'Just(%s)' % repr(self.value)

    def __str__(self):
        return '' if self is Nothing else unicode(self.value)

    def __unicode__(self):
        return u'' if self is Nothing else unicode(self.value)

    def __nonzero__(self):
        return False if self is Nothing else bool(self.value)

    def __call__(self, *args, **kwargs):
        return Nothing if self is Nothing \
            else Maybe(self.value(*args, **kwargs))

    def __getattr__(self, name):
        return Nothing if self is Nothing \
            else Maybe(getattr(self.value, name))

    def __getitem__(self, key_or_slice):
        return Nothing if self is Nothing \
            else Maybe(self.value.__getitem__(key_or_slice))

    def __rshift__(self, fn):
        if self is Nothing:
            return Nothing
        else:
            return fn(self.value)

    def __or__(self, other):
        if self is Nothing:
            return other
        else:
            return self.value

Nothing = Maybe(None)  # actual value here doesn't matter at all
Just = Maybe


if __name__ == '__main__':
    import doctest
    doctest.testmod()
