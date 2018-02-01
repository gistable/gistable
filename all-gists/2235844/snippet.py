NAMES = set()


def replace(old, new):
    """Replace the first function argument.

    If the first function argument matches old it will be Replaced with new.
    """
    # decorate the original function
    def decorate(func):
        # do the replacement using the args of the decorator
        def do_replace(*args, **kwargs):
            if args[0] == old:
                args = (new,)
            # call the decorated function
            return func(*args, **kwargs)
        return do_replace
    return decorate



def remember(func):
    """Remember each name that was called.

    Does only remember each name once.
    """
    # wrap the original function to fetch it's arguments
    def wrapper(*args, **kwargs):
        NAMES.add(args[0])
        # call the decorated function
        return func(*args, **kwargs)
    return wrapper


def check_allowed(func):
    """Check if a function is allowed.

    Returns a function which raises a NameError if a function is not in the
    allowed list.
    """
    allowed = ['say_hi']
    if func.__name__ not in allowed:
        def not_allowed(*args):
            raise NameError('%s not allowed' % func.__name__)
        return not_allowed
    return func


@replace('Paul', 'Paula')
@remember
@check_allowed
def say_hi(name):
    return "Hi %s" % name


def say_hello(name):
    return "Hello %s" % name
say_hello = remember(check_allowed(say_hello))


QUEUE = [
    (say_hi, 'Guido'),
    (say_hello, 'Jason'),
    (say_hi, 'Maria'),
    (say_hello, 'Jeff'),
    (say_hi, 'Paul'),
    (say_hi, 'Guido'),
]
for func, name in QUEUE:
    try:
        print 'Will greet %s' % name
        print func(name)
    except NameError:
        print '%s is not allowed' % name
print 'names used: %s' % ', '.join(NAMES)
