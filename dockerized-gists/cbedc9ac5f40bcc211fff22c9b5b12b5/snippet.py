# decorator function to time functions
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('[TimeIt] func: "{}" run in {}s'.format(method.__name__, te - ts))
        return result
    return timed