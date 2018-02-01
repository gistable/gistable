def accepts(*accepted_types):
    def decorated_function(function):
        def inner(*passed_args):
            for accepted_type, passed_arg in zip(accepted_types, passed_args):
                if not isinstance(passed_arg, accepted_type):
                    raise TypeError
            return function(*passed_args)
        return inner
    return decorated_function


def returns(*return_types, **kwargs):
    allow_none = kwargs.get("allow_none", True)

    if allow_none:
        return_types = return_types + (type(None), )

    def decorated_function(function):
        def inner(*args):
            result = function(*args)
            if not isinstance(result, tuple(return_types)):
                raise TypeError
            return result
        return inner
    return decorated_function


@accepts(int, int)
@returns(int, allow_none=True)
def add(x, y):
    return


print add(1,2)
#print accepts(int, int)(add)(3,2)