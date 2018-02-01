import time

def timeit(fn):
    """
    Time the function execution
    """
    def timmer(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        finish = time.time()
        print('%s function took %0.3f s' % (fn.__name__, (finish - start)))
        return ret
    return timmer

@timeit
def foo(num, word):
	print(num ,word)

foo(1, '2')
