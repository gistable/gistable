import warnings

def deprecated(func):
    def new_func(*args, **kwargs):
        warnings.warn('This function is deprecated', DeprecationWarning, 2)
        return func(*args, **kwargs)
    return new_func

@deprecated
def sum(a, b):
    return a + b

r = sum(1, 2)
print r