class skip_if_exception(object):
    '''
    Given an exception type, returns a decorator & context manager
    that will raise SkipTest if that exception type is raised
    '''
    def __init__(self, ExcType):
        self.ExcType = ExcType

    def __call__(self, func):
        return decorator(self.try_func, func)

    def try_func(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except self.ExcType:
            raise SkipTest

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.ExcType):
            raise SkipTest