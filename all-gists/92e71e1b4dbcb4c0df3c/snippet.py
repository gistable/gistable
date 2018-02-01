def random_elsewhere_function():
    raise AttributeError("oops")


class Foo(object):

    @property
    def bar(self):
        random_elsewhere_function()
        return "bar"

    def __getattr__(self, attr):
        error = "{!r} object has no attribute {!r}"
        raise AttributeError(error.format(self.__class__.__name__, attr))


f = Foo()
f.bar
