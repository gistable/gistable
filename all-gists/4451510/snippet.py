from functools import wraps


def title(title=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            g.page_title = title
            return f(*args, **kwargs)
        return decorated_function
    return decorator