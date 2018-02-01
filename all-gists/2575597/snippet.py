class errors_wrapped(object):
    """
    A function decorator to wrap all exceptions in an exception class of
    your choosing.

    Usage:
        @errors_wrapped(MyExceptionClass)
        def my_function(...

    MyExceptionClass should accept this:
        ...
        catch Exception, e:
            raise MyException(e)
    """

    def __init__(self, ecls):
        self.ecls = ecls

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                trace = sys.exc_info()[2]
                raise self.ecls(e), None, trace

        return wrapped
