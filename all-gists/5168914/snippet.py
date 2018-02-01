"""Class-based decorators.

This code was originally published as part of an article at
http://tech.novapost.fr/python-class-based-decorators-en.html

To run this file:

.. code-block:: sh

   wget -O sample.py https://gist.github.com/benoitbryon/5168914/raw/
   python -m doctest -v sample.py

"""
import functools


# First of all, some 'function-based' decorator examples.
def moo(func):
    """This is a function-based decorator.

    >>> @moo
    ... def i_am_a(kind):
    ...     print "I am a {kind}".format(kind=kind)
    >>> i_am_a("duck")
    moo
    I am a duck

    """
    def decorated(*args, **kwargs):
        print 'moo'
        return func(*args, **kwargs)  # Run decorated function.
    return decorated


def speak(word='moo'):
    """This is a configurable function-based decorator.

    >>> @speak('quack')
    ... def i_am_a(kind):
    ...     print "I am a {kind}".format(kind=kind)
    >>> i_am_a("duck")
    quack
    I am a duck

    You can use this decorator with empty parenthesis:

    >>> @speak()
    ... def i_am_a(kind):
    ...     print "I am a {kind}".format(kind=kind)
    >>> i_am_a("cow")
    moo
    I am a cow

    But you cannot use this decorator without parenthesis:

    >>> @speak
    ... def i_am_a(kind):
    ...     print "I am a {kind}".format(kind=kind)
    >>> i_am_a("duck")  # doctest: +ELLIPSIS
    <function decorated at 0x...>

    """
    def decorator(func):
        def decorated(*args, **kwargs):
            print word
            return func(*args, **kwargs)
        return decorated
    return decorator


# Sentinel to detect undefined function argument.
UNDEFINED_FUNCTION = object()


class Decorator(object):
    """Base class to easily create convenient decorators.

    Override :py:meth:`setup`, :py:meth:`run` or :py:meth:`decorate` to create
    custom decorators:

    * :py:meth:`setup` is dedicated to setup, i.e. setting decorator's internal
      options.
      :py:meth:`__init__` calls :py:meth:`setup`.

    * :py:meth:`decorate` is dedicated to wrapping function, i.e. remember the
      function to decorate.
      :py:meth:`__init__` and :py:meth:`__call__` may call :py:meth:`decorate`,
      depending on the usage.

    * :py:meth:`run` is dedicated to execution, i.e. running the decorated
      function.
      :py:meth:`__call__` calls :py:meth:`run` if a function has already been
      decorated.

    Decorator instances are callables. The :py:meth:`__call__` method has a
    special implementation in Decorator. Generally, consider overriding
    :py:meth:`run` instead of :py:meth:`__call__`.

    This base class transparently proxies to decorated function:

    >>> @Decorator
    ... def return_args(*args, **kwargs):
    ...    return (args, kwargs)
    >>> return_args()
    ((), {})
    >>> return_args(1, 2, three=3)
    ((1, 2), {'three': 3})

    This base class stores decorator's options in ``options`` dictionary
    (but it doesn't use it):

    >>> @Decorator
    ... def nothing():
    ...    pass
    >>> nothing.options
    {}

    >>> @Decorator()
    ... def nothing():
    ...    pass
    >>> nothing.options
    {}

    >>> @Decorator(one=1)
    ... def nothing():
    ...    pass
    >>> nothing.options
    {'one': 1}

    """
    def __init__(self, func=UNDEFINED_FUNCTION, *args, **kwargs):
        """Constructor.

        Accepts one optional positional argument: the function to decorate.

        Other arguments **must** be keyword arguments.

        And beware passing ``func`` as keyword argument: it would be used as
        the function to decorate.

        """
        self.setup(*args, **kwargs)
        #: The decorated function.
        self.decorated = UNDEFINED_FUNCTION
        if func is not UNDEFINED_FUNCTION:
            self.decorate(func)

    def decorate(self, func):
        """Remember the function to decorate.

        Raises TypeError if ``func`` is not a callable.

        """
        if not callable(func):
            raise TypeError('Cannot decorate non callable object "{func}"'
                            .format(func=func))
        self.decorated = func
        return self

    def setup(self, *args, **kwargs):
        """Store decorator's options"""
        self.options = kwargs
        return self

    def __call__(self, *args, **kwargs):
        """Run decorated function if available, else decorate first arg."""
        if self.decorated is UNDEFINED_FUNCTION:
            func = args[0]
            if args[1:] or kwargs:
                raise ValueError('Cannot decorate and setup simultaneously '
                                 'with __call__(). Use __init__() or '
                                 'setup() for setup. Use __call__() or '
                                 'decorate() to decorate.')
            self.decorate(func)
            return self
        else:
            return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        """Actually run the decorator.

        This base implementation is a transparent proxy to the decorated
        function: it passes positional and keyword arguments as is, and returns
        result.

        """
        return self.decorated(*args, **kwargs)


class Greeter(Decorator):
    """Decorator that greets return value of decorated function.

    As a Decorator, you can use it without options.

    >>> @Greeter
    ... def world():
    ...     return 'world'
    >>> world()
    'hello world!'

    The example above is the same as providing empty options.

    >>> @Greeter()
    ... def world():
    ...     return 'world'
    >>> world()
    'hello world!'

    It accepts one ``greeting`` option:

    >>> @Greeter(greeting='goodbye')
    ... def world():
    ...     return 'world'
    >>> world()
    'goodbye world!'

    ``greeting`` option defaults to ``'hello'``:

    >>> my_greeter = Greeter()
    >>> my_greeter.greeting
    'hello'

    You can setup a Greeter instance for later use:

    >>> my_greeter = Greeter(greeting='hi')
    >>> @my_greeter
    ... def world():
    ...     return 'world'
    >>> world()
    'hi world!'

    Which gives you an opportunity to setup the greeter yourself:

    >>> my_greeter = Greeter()
    >>> my_greeter.greeting = 'bonjour'
    >>> @my_greeter
    ... def world():
    ...     return 'world'
    >>> world()
    'bonjour world!'

    All arguments are proxied to the decorated function:

    >>> @Greeter
    ... def name(value):
    ...     return value
    >>> name('world')
    'hello world!'

    >>> @Greeter(greeting='goodbye')
    ... def names(*args):
    ...     return ' and '.join(args)
    >>> names('Laurel', 'Hardy')
    'goodbye Laurel and Hardy!'

    In this example, setup arguments are optional, so, generally, provide them
    with keywords as shown in the examples above. Else, remember that decorated
    function is the first optional argument in ``__init__``:

    >>> @Greeter('what?')  # doctest: +ELLIPSIS
    ... def world():
    ...     return 'world'
    Traceback (most recent call last):
        ...
    TypeError: Cannot decorate non callable object "what?"
    >>> wrong_greeter = Greeter('what?')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: Cannot decorate non callable object "what?"
    >>> ok_greeter = Greeter(lambda: 'world', 'right')
    >>> ok_greeter()
    'right world!'
    >>> another_wrong_greeter = Greeter()
    >>> another_wrong_greeter('what?')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: Cannot decorate non callable object "what?"

    Notice that using class-based decorators makes it quite easy to test if
    a callable has been decorated:

    >>> @Greeter
    ... def world():
    ...     return 'world'
    >>> assert(isinstance(world, Greeter))

    """
    def setup(self, greeting='hello'):
        self.greeting = greeting
        return super(Greeter, self).setup()

    def run(self, *args, **kwargs):
        """Run decorated function and return modified result."""
        name = super(Greeter, self).run(*args, **kwargs)
        return '{greeting} {name}!'.format(greeting=self.greeting, name=name)


class Chameleon(Decorator):
    """A Decorator that looks like decorated function.

    It uses ``functools.update_wrapper``.

    >>> @Chameleon
    ... def documented():
    ...     '''Fake function with a docstring.'''
    >>> documented.__doc__
    'Fake function with a docstring.'

    It accepts options ``assigned`` and ``updated``, that are proxied to
    ``functools.update_wrapper``.

    Default values are ``functools.WRAPPER_ASSIGNMENTS`` for ``assigned`` and
    empty tuple for ``updated``.

    >>> def hello():
    ...    '''Hello world!'''
    >>> wrapped = Chameleon(hello)
    >>> wrapped.assigned
    ('__module__', '__name__', '__doc__')
    >>> wrapped.updated
    ('__dict__',)
    >>> wrapped.__doc__ == hello.__doc__
    True
    >>> wrapped.__name__ == hello.__name__
    True

    >>> only_doc_wrapped = Chameleon(hello, assigned=['__doc__'])
    >>> only_doc_wrapped.__doc__ == hello.__doc__
    True
    >>> only_doc_wrapped.__name__ == hello.__name__  # Doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: 'Chameleon' object has no attribute '__name__'

    >>> hello.__dict__ = {'some_attribute': 'some value'}  # Best on an object.
    >>> attr_wrapped = Chameleon(hello, updated=['__dict__'])
    >>> attr_wrapped.updated
    ['__dict__']
    >>> attr_wrapped.some_attribute
    'some value'

    .. warning::

       Take care of what you pass in ``assigned`` or ``updated``: you could
       break the Chameleon itself. As an example, you should not pass "assigned",
       "run" or "__call__" in ``assigned``, except you know what you are doing.

    """
    def setup(self,
              assigned=functools.WRAPPER_ASSIGNMENTS,
              updated=functools.WRAPPER_UPDATES):
        self.assigned = assigned
        self.updated = updated
        return super(Chameleon, self).setup()

    def decorate(self, func):
        """Make self wrap the decorated function."""
        super(Chameleon, self).decorate(func)
        functools.update_wrapper(self, func,
                                 assigned=self.assigned,
                                 updated=self.updated)
        return self