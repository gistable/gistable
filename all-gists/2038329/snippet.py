from bigfloat import *
N = 5
setcontext(precision(10**N))

def f(x):
    return x + sin(x)

def g(n):
    x = 3
    for i in xrange(n):
        x = f(x)
        
    return x


import sympy
goodpi = str(sympy.pi.evalf(10**N))

def goodtill(n):
    cand = g(n)
    for i,(a,b) in enumerate(zip(str(cand),goodpi)):
        if a != b:
            return i-1
        
inds = range(20)

print map(goodtill,inds)