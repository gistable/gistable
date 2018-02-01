def simple_decorator(func):
    def wrapper(*args, **kwargs):
        condition = True
        if condition:
            return func(*args, **kwargs)
        print('condition else')
        return {'error_code': 1}
    return wrapper


def decorator_with_params(param1=None):
    def func_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if param1 is not None:
                return func(*args, **kwargs)            
            return {'error_code': 1}
        return wrapper
    return func_wrapper



class BaseDecoratorClass(object):
    """ Simple class decorator with params for inherited class."""
    model = None
    owner_field = 'created_by'
    object_id_key = 'id'

    def __init__(self, fun):
        print('init of dec: {}'.format(self.model))
        self.func = fun

    def __call__(self, *args, **kwargs):
        print('call of dec: {}'.format(self.model))
        print('params: {}'.format([self.model, self.owner_field,
                                   self.object_id_key]))
        return self.func(*args, **kwargs)


class ScheduleDecorator(BaseDecoratorClass):
    model = 'Schedule'


class TriggerDecorator(BaseDecoratorClass):
    model = 'Trigger'


@ScheduleDecorator
def foo(test_name):
    print('foo {}'.format(test_name))

@TriggerDecorator
def bar(test_name):
    print('foo {}'.format(test_name))


if __name__ == '__main__':
    foo('aaaa')
    bar('bbbb')