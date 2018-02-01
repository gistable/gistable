from functools import wraps

class tail(object):
    def __init__(self, *args, **kwargs):
        try:
            self.func = args[0]._tail_function
        except AttributeError:
            self.func = args[0]
        self.args = args[1:]
        self.kwargs = kwargs
        
    def __call__(self):
        return self.func(*self.args, **self.kwargs)
        
def tail_recursive(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        while isinstance(f, tail):
            f = f()
        return f
    wrapper._tail_function = func
    return wrapper
    
#Example
@tail_recursive
def rec(x):
    if x <= 0:
        return 1
    else:
        return tail(rec, x-1)