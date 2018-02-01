channels = {}
 
def bind(channel):
    """
    This decorators allows you to define callback functions for certain 'channels'
    """
    def decorate(func):
        channels.setdefault(channel, []).append(func)
        return func
    return decorate
 
def call(channel):
    """
    This decorator allows you to call all bound callback functions when the function is executed.

    Ex:
        @call('my_channel')
        def my_function():
            print("All functions on 'my_channel' will be executed")
    """
    def decorate(func):
        def inner(*args, **kwargs):
            func(*args, **kwargs)
            try:
                for f in channels[channel]:
                    f(*args, **kwargs)
            except KeyError:
                raise ValueError('There is no channel named %s' % channel)
        return inner
    return decorate