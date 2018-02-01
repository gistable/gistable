def dicts(d):
    keys, value_iters = zip(*d.items())
    return (dict(zip(keys,values)) for values in zip(*value_iters))


def property(test_fn=None, tests=100):
    def bind_parameters(test_fn):
        arg_bindings = dicts(test_fn.__annotations__)
        def bound_test_fn():
            for args in itertools.islice(arg_bindings, tests):
                test_fn(**args)
        return bound_test_fn
    
    # Allow @property or @property(tests=<n>)
    return bind_parameters if test_fn is None else bind_parameters(test_fn)
