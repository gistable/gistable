# -*- coding: utf-8 -*-
# a functional is a function that takes a function for its input
def fact(factorial):
    def fn(n):
        if n == 0: return 1
        else:
            return n * factorial(n - 1)
    return fn


def fib1(fib):
    def fn(n):
        if n == 0: return 0
        if n < 2: return 1
        else:
            return fib(n - 2) + fib(n - 1)
    return fn


# Y = λf.(λx.f (x x)) (λx.f (x x))
# Computes the fixed point of a functional, Y(F) = F(Y(F))
def Y(f):
    def inner(cc):
        return f(lambda x: cc(cc)(x))
    return inner(inner)
