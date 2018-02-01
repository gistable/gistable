__author__ = 'jpablo'

##
import operator
from peak.rules import when, abstract


@abstract
def bind(obj, func):
    'do something with obj and func'


def check_left_identity(val, Monad):
    return bind(Monad.wrap(val),f) == f(val)

def check_right_identity(m, Monad):
    return bind(m, Monad.wrap) == m

def check_associativity(m,f,g):
    return bind(m, lambda x: bind(f(x), g)) == bind(bind(m,f), g)



class Identity(object):

    def __init__(self,val):
        self.val = val
        
    def __repr__(self):
        return str(self.val)

    def __eq__(self, other):
        return self.val == other.val

    @staticmethod
    def wrap(val):
        return Identity(val)


## bind / pass / >>=
@when(bind, (Identity,))
def bind_identity(id,func):
    return func(id.val)


print bind(Identity.wrap(1), lambda x: Identity.wrap(x))
print bind(Identity.wrap(1), lambda x: Identity.wrap(x+1))
print bind( Identity.wrap(5), lambda x: bind(Identity.wrap(6), lambda y: Identity.wrap(x+y)))


## indentities

def f(x):
    return Identity(x+1)

def g(y):
    return Identity(y*5)

m = Identity(2)


print check_left_identity(1, Identity)
print check_right_identity(m, Identity)
print check_associativity(m,f,g)


#### array monad ##########

class ListMonad(list):
    @staticmethod
    def wrap(data):
        return ListMonad([data])


def concat(seq):
    return reduce(operator.add, seq, [])


@when(bind, (list,))
def bind_lst(lst, func):
    return concat(map(func,lst))

print bind([1,2,3], lambda x: ListMonad.wrap(x+1))


def f(x): return ListMonad.wrap(x+1)
def g(y): return ListMonad.wrap(y*5)
m = [1,2,3]

print check_left_identity(1, ListMonad)
print check_right_identity(m, ListMonad)
print check_associativity(m,f,g)


def double(val):
    return bind(val, lambda x: val.wrap(x*2))

print double(ListMonad([0,1,2]))
