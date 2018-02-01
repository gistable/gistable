class Bar(object):
    def plop(self):
        print 'plop'

class Foo(object):
    def __init__(self):
        self.bar = Bar()

    def do(self):
        print 'done'

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError as initial:
            try:
                return object.__getattribute__(self.bar, attr)
            except AttributeError:
                raise initial

>>> Foo().do()
done
>>> Foo().plop()
plop
>>> Foo().unexistent
AttributeError: 'Foo' object has no attribute 'unexistent'