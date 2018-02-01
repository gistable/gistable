class Singleton(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


if __name__ == '__main__':
    class Foo(object):
        __metaclass__ = Singleton

    a = Foo()
    b = Foo()

    assert a is b