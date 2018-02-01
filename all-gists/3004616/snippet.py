class StaticMethod(object):
    def __init__(self, func):
        self.func = func


    def __get__(self, obj, cls):
        return self.func


def staticmethod(func):
    return StaticMethod(func)
