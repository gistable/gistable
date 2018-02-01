# Transforming the vanilla recursive fib into the iterative DP version
# through a series of mechanical steps.
#
# For more on converting recursive algorithms into iterative ones, see:
# http://blog.moertel.com/posts/2013-05-11-recursive-to-iterative.html


# original function

def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


# partition the function into base-case logic and incremental logic

def fib(n):
    if n < 2:
        return n
    return step(n)

def step(n):
    return fib(n - 1) + fib(n - 2)


# expand step logic into its fundamental operations

def step(n):
    fibn1 = fib(n - 1)
    fibn2 = fib(n - 2)
    result = fibn1 + fibn2
    return result


# extend step logic with optional arg that eliminates recursion if provided

def step(n, fibn1n2=None):
    if fibn1n2 is not None:
        fibn1, fibn2 = fibn1n2
    else:
        fibn1 = fib(n - 1)
        fibn2 = fib(n - 2)
    result = fibn1 + fibn2
    return result


# make step logic also return its arguments

def fib(n):
    if n < 2:
        return n
    return step(n)[0]  # <-- note [0]

def step(n, fibn1n2=None):
    if fibn1n2 is not None:
        fibn1, fibn2 = fibn1n2
    else:
        fibn1 = fib(n - 1)
        fibn2 = fib(n - 2)
    result = fibn1 + fibn2
    return result, n, fibn1n2  # <-- and, correspondingly, here


# now apply to those returned arguments the *opposite* of the
# transformation that was applied to them in the recursive calls

def fib(n):
    if n < 2:
        return n
    return step(n)[0]

def step(n, fibn1n2=None):
    if fibn1n2 is not None:
        fibn1, fibn2 = fibn1n2
    else:
        fibn1 = fib(n - 1)
        fibn2 = fib(n - 2)
    result = fibn1 + fibn2
    return result, n + 1, (result, fibn1)  # <-- look here


# now the step logic can be run in the *opposite* direction,
# building from the initial conditions upward via iteration;
# we modify the base logic to do this instead of using the
# step logic recursively

def fib(n):
    if n < 2:
        return n
    # initial conditions
    N = n
    n = 2
    fibn1n2 = (1, 0)
    # iterate upward from initial conditions
    while n <= N:
        result, n, fibn1n2 = step(n, fibn1n2)
    return result


# since the step logic is always called with the fibn1n2 argument now,
# make that argument required to simplify the step logic

def step(n, fibn1n2):
    fibn1, fibn2 = fibn1n2
    result = fibn1 + fibn2
    return result, n + 1, (result, fibn1)


# inline the step logic back into the original function

def fib(n):
    if n < 2:
        return n
    # initial conditions
    N = n
    n = 2
    fibn1n2 = (1, 0)
    # iterate upward from initial conditions
    while n <= N:
        fibn1, fibn2 = fibn1n2
        result = fibn1 + fibn2
        result, n, fibn1n2 = result, n + 1, (result, fibn1)
    return result


# simplify

def fib(n):
    if n < 2:
        return n
    fibn1, fibn2 = (1, 0)
    for _ in xrange(2, n + 1):
        result = fibn1 + fibn2
        fibn1, fibn2 = result, fibn1
    return result


# simplify more

def fib(n):
    fibn1, fibn2 = (1, 0)
    for _ in xrange(n):
        fibn1, fibn2 = fibn1 + fibn2, fibn1
    return fibn2


# and we're done!


# tests

def test():
    fns = dict(globals())
    for fname, f in sorted(fns.iteritems()):
        if fname.startswith('fib'):
            print('testing {}'.format(fname))
            assert map(f, range(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
if __name__ == '__main__':
    test()
