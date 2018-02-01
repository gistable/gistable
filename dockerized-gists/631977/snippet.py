# double closures - what does it mean!?
def if_braintree_disabled(default):
    def generate_decorator(f):
        def decorator(*args, **kwargs):
            if not settings.LIVE_SITE and not settings.BRAINTREE_ENABLED:
                return default
            else:
                return f(*args, **kwargs)
        return decorator
    return generate_decorator
