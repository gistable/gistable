import inspect
import cProfile as profile
import wrapt

def prof(*dec_args, **dec_kwargs):
    pr = profile.Profile()
    if not dec_args or not inspect.isfunction(dec_args[0]):
        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            pr.enable()
            result = wrapped(*args, **kwargs)
            pr.disable()
            if dec_kwargs.has_key('filename'):
                pr.dump_stats(dec_kwargs['filename'])
            else:
                pr.print_stats()
            return result
        return wrapper
    else:
        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            pr.enable()
            result = wrapped(*args, **kwargs)
            pr.disable()
            pr.print_stats()
            return result
        return wrapper(dec_args[0])

if __name__ == '__main__':
    import numpy as np

    @prof
    def foo(N):
        return np.linalg.pinv(np.random.rand(N, N))

    @prof(filename='out.prof')
    def bar(N):
        return np.linalg.pinv(np.random.rand(N, N))

    foo(100)
    bar(100)

    # Also works with methods:
    class Foo(object):
        @prof
        def foo(self, N):
            return np.linalg.pinv(np.random.rand(N, N))

    f = Foo()
    f.foo(100)