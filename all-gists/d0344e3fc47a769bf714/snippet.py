# -*- coding:utf-8 -*-
def odd(n):
    return True if n == 1 else even(n - 1)


def even(n):
    return False if n == 1 else odd(n - 1)


def odd2(n):
    return (None, True) if n == 1 else (even2, (n - 1))


def even2(n):
    return (None, False) if n == 1 else (odd2, (n - 1))


def trampoline(f, n):
    while f is not None:
        f, n = f(n)
    return n

print(trampoline(odd2, 1000000))
try:
    print(odd(1000000))
except RuntimeError:
    print("oops")
