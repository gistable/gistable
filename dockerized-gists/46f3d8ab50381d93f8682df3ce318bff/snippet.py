import time
from functools import wraps

timeout_funcs = {}


def get_seconds():
    return int(round(time.time()))


def timeout(duration):
    def check(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if func not in timeout_funcs or timeout_funcs[func] < get_seconds():
                timeout_funcs[func] = get_seconds() + duration
                return func(*args, **kwargs)

            func_name = func.__name__

            try:
                update = args[1]
                msg = "/{} is timed out for {} seconds after you called it.". \
                      format(func_name, duration)
                update.message.reply_text(msg)
            except (IndexError, AttributeError):
                msg = "Check if you spelled the attributes right and if this is \
                        applied on the right function."
                raise Exception(msg)

        return inner
    return check