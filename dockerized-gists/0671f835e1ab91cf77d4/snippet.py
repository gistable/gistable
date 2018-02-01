import types


class ClassMethod(object):

    def __init__(self, func):
        self.__func__ = func

    def __get__(self, obj, objtype=None):
        return types.MethodType(self.__func__, objtype or type(obj), type)


def class_method(func):
    return ClassMethod(func)


class StaticMethod(object):

    def __init__(self, func):
        self.__func__ = func


    def __get__(self, obj, objtype=None):
        return self.__func__


def static_method(func):
    return StaticMethod(func)