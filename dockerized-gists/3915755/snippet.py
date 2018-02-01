from functools import wraps

def OneUndo(function):
    @wraps(function)
    def _decorated(*args, **kwargs):
        try:
            Application.BeginUndo()
            f = function(*args, **kwargs)
        finally:
            Application.EndUndo()
            return f
    return _decorated