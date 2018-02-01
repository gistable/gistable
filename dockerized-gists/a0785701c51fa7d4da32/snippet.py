class WeakProperty:
    """Descriptor that automatically holds onto whatever it contains as a weak
    reference.  Reading this attribute will never raise `AttributeError`; if
    the reference is broken or missing, you'll just get `None`.

    The actual weak reference is stored in the object's `__dict__` under the
    given name, so this acts as sort of a transparent proxy that lets you
    forget you're dealing with weakrefs at all.

    Of course, if you try to assign a value that can't be weak referenced,
    you'll get a `TypeError`.  So don't do that.

    Example:

        class Foo:
            bar = WeakProperty('bar')

        obj = object()
        foo = Foo()
        foo.bar = obj
        print(foo.bar)  # <object object at ...>
        assert foo.bar is obj
        del obj
        print(foo.bar)  # None

    Note that due to the `__dict__` twiddling, this descriptor will never
    trigger `__getattr__`, `__setattr__`, or `__delattr__`.
    """
    def __init__(self, name):
        self.name = name

    def __get__(desc, self, cls):
        if self is None:
            return desc

        try:
            ref = self.__dict__[desc.name]
        except KeyError:
            return None
        else:
            value = ref()
            if value is None:
                # No sense leaving a dangling weakref around
                del self.__dict__[desc.name]
            return value

    def __set__(desc, self, value):
        self.__dict__[desc.name] = weakref.ref(value)

    def __delete__(desc, self):
        del self.__dict__[desc.name]
