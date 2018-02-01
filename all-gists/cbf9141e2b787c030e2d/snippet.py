from functools import wraps


def trigger_decorator(trigger_on):
    @wraps(trigger_on)
    def specifec_method(self, name):
        def decorator(trigger_func):
            # This is what **outside** see
            # A function which 
            # returned decorator as trigger
            @wraps(trigger_func)
            def decorator_to_outer_func(api_func):
                @wraps(api_func)
                def generated_wrapped(*args, **kwargs):
                    response = trigger_on(trigger_func, api_func, *args, **kwargs)
                    # response_after_trigger = trigger_func(api_func, *args, **kwargs )
                    return response
                return generated_wrapped
            # Here exposed to outside
            self.add_trigger(name, decorator_to_outer_func)
            # return trigger_func so that we can chain
            return trigger_func             
        return decorator
    return specifec_method


class Trigger(object):
    def __init__(self):
        self.trigger_map = {}

    def register(self, name):
        def func_wrapper(func):
            self.trigger_map[name] = func
            return func
        return func_wrapper

    @trigger_decorator
    def before(trigger_func, api_func, *args, **kwargs):
        trigger_func(*args, **kwargs)
        return api_func(*args, **kwargs)

    @trigger_decorator
    def around(trigger_func, api_func, *args, **kwargs):
        return trigger_func(api_func, *args, **kwargs)

    @trigger_decorator
    def after(trigger_func, api_func, *args, **kwargs):
        response = api_func(*args, **kwargs)
        return trigger_func(response, *args, **kwargs)

    def get_trigger(self, name):
        func_list = self.trigger_map[name]
        def apply_all(api_func):
            return reduce(lambda func, trigger: trigger(func), func_list, api_func)
        return apply_all

    def add_trigger(self, name, func):
        if self.trigger_map.get(name) is None:
            self.trigger_map[name] = []
        self.trigger_map[name].append(func)

trigger = Trigger()





if __name__ == '__main__':
    def sample_api(user, *args, **kwargs):
        print 'Inside sample API. User is:',user
        return 'sample_api_result'


    @trigger.around('/rest/api/2')
    def auth(fn, user, *args, **kwargs):
        print 'Inside Trigger.'

        if user == 'Admin':
            print 'Yes It\' Admin'
        print 'before func'
        ret = fn(user=user, *args, **kwargs)
        print 'after func:', ret
        return ret


    @trigger.before('/rest/api/2')
    @trigger.before('/rest/api/2')
    def before(*args, **kwargs):
        print 'In Before Trigger'


    @trigger.after('/rest/api/2')
    def after(response, *args, **kwargs):
        print 'After Trigger'
        return response

    dec = trigger.get_trigger('/rest/api/2')
    func = dec(sample_api)

    ret= func('Admin')
    print '========ReturnValue=========='
    print ret
