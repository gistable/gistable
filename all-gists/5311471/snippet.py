#! /usr/bin/python
"""Implementation of the arrow abstraction for functions.

Abstracting functions with Arrows has advantages.  Arrows make it very easy to
compose functions (by simply 'multiplying' them with the `*` operator).  The
order in which the arrows are written match the order of the computations,
making long pipelines easy to work with.  Arrows also provide mechanisms for
creating and merging branches, which helps when a value needs to be consumed by
several functions, or when a function needs values from several sources. Arrows
can also support conditional application, selecting which of two functions f and
g must be applied to x depending on a boolean b.

I designed this module so that we can express complex pipelines in a condensed
way.  To achieve that goal, I make a heavy use of operators such as +, -, *, /,
>>, etc.  Because the number of operators in Python is limited, and because
their precedence cannot be modified, I had to make a choice that was a
compromise between readability and usability.

>>> addOne = Arrow(lambda x : x + 1)
>>> double = Arrow(lambda x : x * 2)
>>> square = Arrow(lambda x : x ** 2)
>>> sqrt = lambda x : x ** .5 # Not an arrow, on purpose.
>>> from operator import add

>>> 10 >> addOne ** 5 * square - double * square
(225, 400)
>>> 10 >> (addOne ** 5 * square - double * square) / add
625
>>> 10 >> (addOne ** 5 * square - double * square) / add % sqrt
25.0
>>> 10 >> addOne - double - square
((11, 20), 100)
>>> 10 >> ((addOne - double) / add - square) / add
131

Note that you can use `Arrow` as a decorator:
>>> @Arrow
... def addTwo(x):
...     return x + 2
>>> 10 >> addTwo
12

"""

from __future__ import division

class Arrow(object):
    def __init__(self, func):
        if not hasattr(func, '__call__'):
            raise TypeError("Arrow parameter should be callable; %r is not." % func)
        object.__init__(self)
        self.func = func
    def __div__(self, _):
        raise ImportError("For Arrows to work, Python3's divisions must be enabled.  Use ''from __future__ import division''.")
    def __mul__(self, other):
        """Arrow composition.

        --> self --> other -->

        Mnemonic: In algebra, multiplying matrices is equivalent to composing
        linear functions.
        
        Like function composition, arrow composition is not commutative.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> addOne * double
        22
        >>> 10 >> double * addOne
        21

        """
        return Arrow(compose(self.func, other.func))
    def __floordiv__(self, other):
        """Arrow composition on pairs of inputs.

        Used when an arrow must be used on both elements of the 2-tuple input.

                  |--> other -->|
        > self ==>|             |==>
                  |--> other -->|

        f *= g  ==  f * (g + g)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> square = Arrow(lambda x : x ** 2)
        >>> 10 >> (double - square) // addOne
        (21, 101)

        """
        return self * (other + other)
    def __mod__(self, other):
        """ Arrow composition with a pure function after.

        --> self --> other -->

        If f and g are pure functions, then
        Arrow(f) % g  ==  Arrow(f) * Arrow(g)

        Mnemonic: The two circles of the % symbol remind you that on one side
        is an arrow, and the other side is a pure function.
        
        >>> addOne = Arrow(lambda x : x + 1)
        >>> 10 >> addOne % (lambda x : x * 2)  # This lambda is not an arrow.
        22

        """
        return self * Arrow(other)
    def __rmod__(self, other):
        """Arrow composition with a pure function before.

        --> other --> self -->

        If f and g are pure functions, then
        f % Arrow(g)  ==  Arrow(f) * Arrow(g)

        Note that the direction of the data flow (from left to right) is
        preserved, since `other` appears before `self` in the code.  It's just
        that `other` is a pure function that doesn't support `__mod__`, so
        `__rmod__` of the following object (self) kicks in.

        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> (lambda x : x + 1) % double  # This lambda is not an arrow.
        22

        """
        return Arrow(other) * self
    def __add__(self, other):
        """Parallel application on two inputs yielding two outputs.

        Apply self to the first element of a 2-tuple, and other to the second
        element of that 2-tuple.

           |--> self -->|
        ==>|            |==>
           |--> other ->|

        (x, y) >> f + g = (f x, g y)

        Mnemonic: The + sign means that we process many inputs at once.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (5, 10) >> addOne + double
        (6, 20)

        """
        return Arrow(lambda x:(self.func(x[0]), other.func(x[1])))
    def __sub__(self, other):
        """Parallel application on one input yielding two outputs.

        The input is duplicated and fed to each arrow.

           |--> self -->|
        -->|            |==>
           |--> other ->|

        x >> f - g = (f x, g x)

        This is equivalent to: (lambda x : (x, x)) % (f + g)

        Mnemonic: The - sign means that we process a single input.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> addOne - double
        (11, 20)

        """
        return Arrow(lambda x:(self.func(x), other.func(x)))
    def __truediv__(self, other):
        """Combine two inputs into one output with the pure function `other`.
        
        This allows joining the two outputs of an arrow created by + or -.
        This operator is provided for convenience and is equivalent to
        self % uncurry(other)

        > self ==> other -->
        
        Mnemonic: The division sign means that we divide the number of
        parameters by two.  This is definitely not the opposite of *.
        
        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> plus = lambda a, b: a + b  # Or import operator.add.
        >>> 10 >> (addOne - double)
        (11, 20)
        >>> 10 >> (addOne - double) / plus
        31

        """
        return self % uncurry(other)
    def __pow__(self, n):
        """Repeated composition.
        
        Compose the arrow `n` times, `n` being a natural number.
        > self --> self --> self..., n times.

        f ** 3 == f * f * f

        >>> 10 >> Arrow(lambda x : x + 1) ** 3
        13

        If n <= 0, returns the identity arrow.

        >>> 10 >> Arrow(lambda x : x + 1) ** 0
        10

        """
        if n <= 0:
            return identityA
        return self * self ** (n - 1)
    def __rrshift__(self, other):
        """Arrow application.
        
        Makes the arrow compute a result from the given input.
        
        x >> F, where F is an arrow of a pure function f, is equivalent to
        f(x).
        
        >>> 10 >> Arrow(lambda x : x + 1)
        11
        
        """
        return self.func(other)
    def __or__(self, other):
        """Chooses an arrow depending on the truth of the first value.

        (False, x) >> (f | g) == x >> f
        (True , x) >> (f | g) == x >> g

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (False, 10) >> (addOne | double)
        11
        >>> (True, 10) >> (addOne | double)
        20

        Note that | has a lower precedence than >>, hence the parentheses.
        Theses can be avoided by naming the arrow.
        >>> choice = addOne | double
        >>> (True, 10) >> choice
        20

        Note that it is possible to chain choices if f and g produce tuples.
        
        >>> testOddity = Arrow(lambda x: (bool(x % 2), 'odd'))
        >>> testPositivity = Arrow(lambda x: (x >= 0, 'positive'))
        >>> testSomething = testOddity | testPositivity
        
        Here, False says we test for oddity, and 4 is even, so the output is
        False.

        >>> (False, 4) >> testSomething
        (False, 'odd')

        We are still testing for oddity and -5 is odd, so the output is True.

        >>> (False, -5) >> testSomething
        (True, 'odd')

        We test for positivity (first element is True). 4 is positive but -5 is
        not.

        >>> (True, 4) >> testSomething
        (True, 'positive')
        >>> (True, -5) >> testSomething
        (False, 'positive')

        In this example, the second element of the 2-tuple is a constant
        (string) provided by testOddity or testPositivity, but it can be
        anything more interesting that can depend on x.  This example was just
        an illustration of how to use | to produce another 2-tuple (Bool,
        value) suitable for another |.

        """
        return Arrow(lambda (b, x) : other.func(x) if b else self.func(x))

def identity(x):
    return x
identityA = Arrow(identity)

def compose(f, g):
    """Pure function composition.

    compose(f, g)(x) = g(f(x))

    Note that I don't compose in the usual order seen in methematics.
    Composition is usually (f o g)(x) = f(g(x)).  I don't like that, because
    it's not in the same order as the arrows for which computations flow from
    left to right.  When I see (f o g), I want to apply f first, and then g.

    """
    return lambda x:g(f(x))

def curry(f):
    """Make a function that needs a 2-tuple accept two parameters instead."""
    return lambda x, y : f((x, y))

def uncurry(f):
    """Make a function that needs two parameters accept a 2-tuple instead."""
    return lambda (x, y) : f(x, y)

def replicate(n):
    return Arrow(lambda x : [x] * n)

def dup(x):
    return (x, x)

def swap(x, y):
    return (y, x)

def tupledown(((a, b), c)):
    return (a, (b, c))

def tupleup((a, (b, c))):
    return ((a, b), c)

def unzip(x):
    return zip(*x)

def firsta(f):
    """Create an Arrow from a pure function that applies to the first element
    of a 2-tuple.

    This is equivalent to Arrow(f) + identityA.

    >>> (1, 10) >> first(lambda x:x+1)
    (2, 10)

    """
    return firstA(Arrow(f))

def firstA(a):
    return a + identityA

def seconda(f):
    """Create an Arrow from a pure function that applies to the second element
    of a 2-tuple.

    This is equivalent to Arrow(f) + identityA.

    >>> (1, 10) >> second(lambda x:x+1)
    (1, 11)

    """
    return secondA(Arrow(f))

def secondA(a):
    return identityA + a

def fst((x, _)):
    return x

def snd((_, y)):
    return y

def mapa(f):
    """Version of map that works like an arrow.

    >>> [2, 3, 5, 7, 11] >> mapa(lambda x : x + 1)
    [3, 4, 6, 8, 12]

    """
    return Arrow(lambda xs : map(f, xs))

def mapA(a):
    """Version of map that works like an arrow and takes an arrow instead of a
    function.

    >>> addOne = Arrow(lambda x : x + 1)
    >>> [2, 3, 5, 7, 11] >> mapA(addOne)
    [3, 4, 6, 8, 12]

    """
    return mapa(a.func)

def reducea(f, z):
    """Version of reduce (fold) that works like an arrow.

    >>> from operator import add
    >>> [2, 3, 5, 7, 11] >> reducea(add, 0)
    28

    `z` stands for "zero", it initializes the reduction.

    >>> [2, 3, 5, 7, 11] >> reducea(lambda s, n : s + str(n), '')
    '235711'

    """
    return Arrow(lambda xs : reduce(f, xs, z))

def mapplya(functions):
    """Apply a list of functions to a list of inputs, works like an arrow.

    >>> addOne = lambda x : x + 1
    >>> double = lambda x : x * 2
    >>> square = lambda x : x ** 2
    >>> [3, 5, 7] >> mapplya([addOne, double, square])
    [4, 10, 49]

    You can start from a single value that way:
    >>> def replicate(n):
    ...    return lambda x : [x] * n
    >>> 10 >> replicate(3) % mapplya([addOne, double, square])
    [11, 20, 100]

    In many cases you will want to use this instead of the + and - operators,
    which are limited to only two values and can be a pain to combine when used
    many times.

    """
    return Arrow(lambda xs: [f(x) for f, x in zip(functions, xs)])

def mapplyA(arrows):
    """Apply a list of arrows to a list of inputs, works like an arrow.

    >>> addOne = Arrow(lambda x : x + 1)
    >>> double = Arrow(lambda x : x * 2)
    >>> square = Arrow(lambda x : x ** 2)
    >>> [3, 5, 7] >> mapplyA([addOne, double, square])
    [4, 10, 49]

    You can start from a single value that way:
    >>> def replicate(n):
    ...    return lambda x : [x] * n
    >>> 10 >> replicate(3) % mapplyA([addOne, double, square])
    [11, 20, 100]

    In many cases you will want to use this instead of the + and - operators,
    which are limited to only two values and can be a pain to combine when used
    many times.

    """
    return mapplya([a.func for a in arrows])

def rmapplya(functions):
    """Like mapplya, but replicate the input first."""
    return replicate(len(functions)) * mapplya(functions)

def rmapplyA(arrows):
    """Like mapplyA, but replicate the input first."""
    return replicate(len(arrows)) * mapplyA(arrows)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
