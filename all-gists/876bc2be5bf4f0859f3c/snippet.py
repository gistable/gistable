# I glanced through the pycket paper, saw few rules there. Ended up to doing this.

class Var(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Lam(object):
    def __init__(self, bind, expr):
        self.bind = bind
        self.expr = expr

    def __repr__(self):
        return "({}.{})".format(self.bind, self.expr)

class Call(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return "({} {})".format(self.lhs, self.rhs)

class Env(object):
    def __init__(self, parent, bind, expr):
        self.parent = parent
        self.bind = bind
        self.expr = expr

    def __call__(self, var):
        if self.bind is var:
            return self.expr
        return self.parent(var)

    def __repr__(self):
        return "{}:{};{}".format(self.bind, self.expr, self.parent)

class Arg(object):
    def __init__(self, expr, env, cont):
        self.expr = expr
        self.env = env
        self.cont = cont

    def __repr__(self):
        return "arg({}, {})::{}".format(self.expr, self.env, self.cont)

class Fun(object):
    def __init__(self, expr, env, cont):
        self.expr = expr
        self.env = env
        self.cont = cont

    def __repr__(self):
        return "fun({}, {})::{}".format(self.expr, self.env, self.cont)

def step(expr, env, cont):
    if isinstance(expr, Var):
        return env(expr), env, cont
    if isinstance(expr, Call):
        return expr.lhs, env, Arg(expr.rhs, env, cont)
    if isinstance(expr, Lam) and isinstance(cont, Arg):
           return cont.expr, cont.env, Fun(expr, env, cont.cont)
    if isinstance(cont, Fun):
       return cont.expr.expr, Env(cont.env, cont.expr.bind, expr), cont.cont
    assert False

x = Var('x')
y = Var('y')
z = Var('z')
env = None
expr = Call(Call(Lam(y, Lam(z, Call(y, 10))), Lam(x, 5)), 12)
cont = None
while True:
    print expr, env, cont
    expr, env, cont = step(expr, env, cont)