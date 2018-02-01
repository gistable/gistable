from types import FunctionType
import inspect

def undecorate(func):
    funcs = []
    
    # python 3.5
    if hasattr(func, '__wrapped__'):
        while hasattr(func, '__wrapped__'):
            func = func.__wrapped__
        return func

    # For py 2.7
    elif hasattr(func, '__closure__'):
        closures = list(c.cell_contents for c in func.__closure__
                        if c.cell_contents is not None)

        # Let's try returning the first closure that is a function object
        funcs = list(c for c in closures if isinstance(c, FunctionType))

    # If it doesn't have __closure__ or we were unable to find a correct closure
    elif len(funcs) == 0: 
        raise NotImplementedError("Sorry you are out of luck. I don't handle this func")

    return funcs[0]