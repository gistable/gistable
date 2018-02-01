def debounced_wrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = kwargs.pop("key")  # it's required
        call_count = kwargs.pop("call_count", 1)
        count = cache.get(key, 1)
        if count > call_count:
            # someone called the function again before the this was executed
            return None
        # I'm the last call
        return func(*args, **kwargs)
    return wrapper


def debounced_task(key_generator):
    """
    :param func: must be the @debounced_wrap decorated with @task / @shared_task from celery
    :param key_generator: function that knows how to generate a key from
    args and kwargs passed to func or a constant str used in the cache
    key will be prepended with function module and name
    :return: function that calls apply_async on the task keep that in mind when send the arguments
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            func_args = kwargs.get("args", [])
            func_kwargs = kwargs.get("kwargs", {})
            key = "{}.{}.{}".format(
                func.__module__,
                func.__name__,
                key_generator(*func_args, **func_kwargs)
            )
            cache.add(key, 0)
            call_count = cache.incr(key)
            func_kwargs.update(
                {
                    'key': key,
                    'call_count': call_count
                }
            )
            kwargs['args'] = func_args
            kwargs['kwargs'] = func_kwargs
            return func.apply_async(**kwargs)
        return wrapper
    return decorator

"""
Usage example

@debounced_task(lambda x, *a, **k: x)
@shared_task
@debounced_wrap
def send_email(user_id, email_id):
    get_user(user_id).email(email_id)

send_email(args=[1], kwargs={'email_id': 2}, countdown=10)
send_email(args=[1], kwargs={'email_id': 2}, countdown=10)
send_email(args=[1], kwargs={'email_id': 2}, countdown=10)
send_email(args=[1], kwargs={'email_id': 2}, countdown=10) # Only this one will execute

"""