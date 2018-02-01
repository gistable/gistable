

class switch(object):
    def __init__(self, expr):
        self.expr = expr
        self.cases = {}
        self._default = None

    def __call__(self, expr):

        def inner(f):
            self.cases[expr] = f
            return f

        return inner           

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.cases.get(self.expr, self._default)()

    def default(self, f):
        self._default = f
        return f


x = 1

with switch(x) as case:

    @case(1)
    def f():
        print 'case 1'

    @case(2)
    def f():
        print 'case 2'

    @case.default
    def f():
        print 'default'
