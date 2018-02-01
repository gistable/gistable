def persist_cache_to_disk(filename):
    def decorator(original_func):
        try:
            cache = pickle.load(open(filename, 'r'))
        except (IOError, ValueError):
            cache = {}

        atexit.register(lambda: pickle.dump(cache, open(filename, "w")))

        def new_func(*args):
            if tuple(args) not in cache:
                cache[tuple(args)] = original_func(*args)
            return cache[args]

        return new_func

    return decorator

# example use of the decorator    
@persist_cache_to_disk('users.p')
def get_all_users():
	# your method here
	pass