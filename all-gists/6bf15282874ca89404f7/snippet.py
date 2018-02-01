def multi(dispatch_fn):
    def _inner(*args, **kwargs):
        return _inner.__multi__.get(
            dispatch_fn(*args, **kwargs),
            _inner.__multi_default__
        )(*args, **kwargs)

    _inner.__multi__ = {}
    _inner.__multi_default__ = lambda *args, **kwargs: None  # Default default
    return _inner

def method(dispatch_fn, dispatch_key=None):
    def apply_decorator(fn):
        if dispatch_key is None:
            # Default case
            dispatch_fn.__multi_default__ = fn
        else:

            dispatch_fn.__multi__[dispatch_key] = fn
        return dispatch_fn
    return apply_decorator


# Dispatch on types


class Person(object):
    def __init__(self, name):
        self.name = name

@multi
def get_name(obj):
    return obj.__class__

@method(get_name, dict)
def get_name(obj):
    return obj['name']

@method(get_name, Person)
def get_name(obj):
    return obj.name

@method(get_name)  # Default
def get_name(*args, **kwargs):
    return "No name"


get_name(Person('Steve'))  # => Steve
get_name({'name': 'Tom'})  # => Tom
get_name(2)  # => No name


@multi
def area(shape):
    return shape.get('type')

@method(area, 'square')
def area(square):
    return square['width'] * square['height']

@method(area, 'circle')
def area(circle):
    return circle['radius'] ** 2 * 3.14159

@method(area)
def area(unknown_shape):
    raise Exception("Can't calculate the area of this shape")


area({'type': 'circle', 'radius': 0.5})  # => 0.7853975
area({'type': 'square', 'width': 1, 'height': 1})  # => 1
area({'type': 'rhombus'})  # => throws Exception