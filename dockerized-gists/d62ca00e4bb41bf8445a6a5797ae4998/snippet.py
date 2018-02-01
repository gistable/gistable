
class Expr(object):
    def __init__(self):
        raise NotImplementedError
    def eval(self):
        raise NotImplementedError

class Value(Expr):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

    def __str__(self):
        return str(self.value)

class Minus(Expr):
    def __init__(self, expr):
        self._expr = expr

    def eval(self):
        return self._expr.eval() * -1

    def __str__(self):
        return "-{0}".format(str(self._expr))


class BinOp(Expr):
    def __init__(self, a, b, f, fstr):
        self._a = a
        self._b = b
        self._op = f
        self._opstr = fstr

    def eval(self):
        return self._op(self._a.eval(), self._b.eval())

    def __str__(self):
        return "{1} {0} {2}".format( str(self._opstr), str(self._a), str(self._b))

class Add(BinOp):
    def __init__(self, a, b):
        super(Add, self).__init__(a, b, (lambda x,y: x + y), "+")


def add(x,y):
    return BinOp(x,y,lambda a,b : a + b, "+")


class Mul(BinOp):
    def __init__(self, a, b):
        super(Mul, self).__init__(a, b, (lambda x,y: x * y), "*")

class Sub(Add):
    def __init__(self, a, b):
        super(Sub, self).__init__(a, Minus(b))


def eval(expr):
    return expr.eval()

def main():
    for e in [ add(Minus(Value(4)), Value(5)) \
             , Add(Minus(Value(4)), Value(5)) \
             , Sub(Minus(Value(4)), Minus(Value(4))) \
             ]:
        print str(e)
        print eval(e)

if __name__ == '__main__':
    main()

