def optional_arg_decorator(fn):
    """
    wrap a decorator so that it can optionally take args/kwargs
    when decorating a func
    """
    # http://stackoverflow.com/a/32292739/2156113
    @wraps(fn)
    def wrapped_decorator(*args, **kwargs):
        is_bound_method = args and hasattr(args[0], fn.__name__)

        if is_bound_method:
            klass, args = args[0], args[1:]

        # If no arguments were passed...
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            if is_bound_method:
                return fn(klass, args[0])
            else:
                return fn(args[0])

        else:
            def real_decorator(decoratee):
                if is_bound_method:
                    return fn(klass, decoratee, *args, **kwargs)
                else:
                    return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator