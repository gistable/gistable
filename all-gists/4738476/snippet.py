import inspect 

class AttributesProxy(object):
    __fields = None

    def __init__(self, instance):
        self.__instance = instance
    
    def __getattr__(self, name):
        attr = getattr(self.__instance, name)
        if inspect.ismethod(attr):
            raise AttributeError
        elif self.__fields is None:
            return attr
        elif name in self.__fields:
            return attr
        else:
            raise AttributeError
    
    def __setattr__(self, name, value):
        if name == "_AttributesProxy__instance":
            super(AttributesProxy, self).__setattr__(name, value)
        else:
            raise NotImplementedError
