import itertools

# Microkanren programs are 'goal' functions that take in a
# state and return a stream of states that satisfy the given goal.

# I am interested about microkanren because it presents a logic
# programming kernel which fits into a dynamically typed language.

# Anything could go as a variable, but I wanted names for variables.
class Variable(object):
    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return self.name or '<{}>'.format(id(self))

# State consists of unification results, it can be simple such as an assoc list.
def load(st, var):
    if isinstance(var, Variable):
        for key, value in reversed(st):
            if key is var:
                if isinstance(value, Variable):
                    return load(st, value)
                return value
    return var

# Equality, conjunction and disjunction are goal constructors..
def eq(a_, b_):
    def _impl_(st):
        a = load(st, a_)
        b = load(st, b_)
        if a is b: # not want to grow state with (a, a) -associations.
            yield st
        elif isinstance(a, Variable):
            yield st + [(a, b)] # The only place where state can grow.
        elif isinstance(b, Variable):
            yield st + [(b, a)]
        elif isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b) > 0:
            for fn in reduce(conj, [eq(x, y) for x, y in zip(a, b)]):
                for st in fn(st): # Tuple unification treated as: (a,b)=(b,c) -> {a=b, b=c}
                    yield st
        elif a == b:
            yield st
    return _impl_

# Conj is bit like AND and Disj bit like OR.
def conj(x, y):
    def _impl_(st):
        for st in x(st):
            for st in y(st):
                yield st
    return _impl_

def disj(x, y):
    def _impl_(st):
        xs = x(st)
        ys = y(st)
        for xst, yst in itertools.izip(xs, ys):
            yield xst
            yield yst
        for xst in xs:
            yield xst
        for yst in ys:
            yield yst
    return _impl_

# Say I'd like to write an assembler using microkanren..
def cat(oktet_, e_, f_):
    def _impl_(st):
        oktet = load(st, oktet_)
        e = load(st, e_)
        f = load(st, f_)
        if isinstance(f, str):
            return conj(eq(oktet, ord(f[0])), eq(e, f[1:]))(st)
        elif isinstance(e, str) and isinstance(oktet, int):
            return eq(chr(oktet) + e, f)(st)
        return iter(())
    return _impl_

def byt(oktet):
    def _impl(e, f):
        return cat(oktet, e, f)
    return _impl

def pat(*patterns):
    def _impl_(e, f):
        goals = []
        for pattern in reversed(patterns):
            t = Variable()
            goals.append(pattern(t, f))
            f = t
        goals.append(eq(e, f))
        return reduce(conj, reversed(goals))
    return _impl_

if __name__=='__main__':
    a = ""
    b = Variable('b')
    c = Variable('c')
    k = Variable('k')
    goal = pat(byt(k), byt(124), byt(125))(a, b)
    goal = conj(disj(
            eq(k, 124),
            eq(k, 125),
        ), conj(goal, disj( 
            conj(eq(k, 124), byt(5)(b, c)),
            conj(eq(k, 125), byt(6)(b, c)),
            )))
    for st in goal([]):
        print st
    print 'test'
    # ..hmm. This is not sufficient.

    oktet = Variable('oktet')
    postfix = Variable('postfix')

    for st in cat(oktet, postfix, "xyz")([]):
        print st
    for st in cat(ord("x"), "yz", "xyz")([]):
        print st
    for st in cat(oktet, "yz", "xyz")([]):
        print st

    midfix = Variable('midfix')
    for st in conj(eq(oktet, ord("x")), conj(cat(oktet, "yz", midfix), cat(oktet, midfix, postfix)))([]):
        print st


    x = Variable('x')
    y = Variable('y')
    z = Variable('z')
    for st in conj(eq(x, 5), disj(eq(x, y), eq(x, z)))([]):
        print st
