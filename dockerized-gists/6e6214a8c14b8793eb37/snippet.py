def memoize_to_file(func=None, **options):
    """Wraps a function definition so that if the function is ever
    called with the same arguments twice, the results are pulled from
    a cache stored in a file. The filename is specified when decorating
    the memoized function. Iterable objects like dicts, lists or
    pandas DataFrames are cast to a tuple before being hashed, and
    everything else uses the object's __repr__ definition.

    Usage:

        (in Python)
        @memoize_to_file(filename='/tmp/my_personal_dump')
        def really_long_running_function(some_weird_input):
            ...

        really_long_running_function(weird_input_1)  # takes forever
        really_long_running_function(weird_input_1)  # takes no time at all!
        really_long_running_function(weird_input_2)  # different arg = long time

        (in bash)
        $ rm -rf /tmp/my_personal_dump*

        (back in Python)

        really_long_running_function(weird_input_1)  # takes forever again
        really_long_running_function(weird_input_1)  # takes no time at all!


    """
    # Check whether it was called with optional arguments
    if func is not None:
        @wraps(func)
        def inner(*args, **kwargs):
            filename = options.get('filename', '/tmp/memoize')
            cache_filename = '{}_{}.pkl'.format(filename, func.func_name)
            cache = {}
            try:
                with open(cache_filename, 'r') as cache_file:
                    cache = pickle.load(cache_file)
            except Exception:
                pass

            def is_panda_df_like(obj):
                return hasattr(obj, 'values')

            def generate_immutable_objects(a_list):
                for item in a_list:
                    if is_panda_df_like(item):
                        yield tuple(map(tuple, item.values))
                    else:
                        try:
                            yield tuple(item)
                        except TypeError:
                            yield repr(item)

            def make_dict_immutable(a_dict):
                return tuple(a_dict.keys()), tuple(generate_immutable_objects(a_dict.itervalues()))

            immutable_args = tuple(generate_immutable_objects(args)), make_dict_immutable(kwargs)
            cache_key = hash(immutable_args)

            if cache_key in cache:
                return cache[cache_key]
            else:
                results = func(*args, **kwargs)
                with open(cache_filename, 'w') as cache_file:
                    cache[cache_key] = results
                    pickle.dump(cache, cache_file)
                    return results
        return inner
    else:
        def partial_inner(func):
            return memoize_to_file(func, **options)
        return partial_inner