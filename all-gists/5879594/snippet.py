import cProfile

from functools import wraps
from time import time


def benchmark(iterations=10000):
    def wrapper(function):
        @wraps(function)
        def func(*args, **kwargs):
            t1 = time()
            for i in range(iterations):
                call = function(*args, **kwargs)
            t2 = time()
            t3 = int(1 / ((t2 - t1) / iterations))
            print func.func_name, 'at', iterations, 'iterations:', t2 - t1
            print 'Can perform', t3, 'calls per second.'
            return call
        return func
    return wrapper


'''
isqrt_1 at 10000 iterations: 12.25
Can perform 816 calls per second.
         10006 function calls in 12.904 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   12.904   12.904 <string>:1(<module>)
        1    0.690    0.690   12.904   12.904 math.py:10(func)
    10000   12.213    0.001   12.213    0.001 math.py:24(isqrt_1)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {range}
        2    0.000    0.000    0.000    0.000 {time.time}
'''
@benchmark()
def isqrt_1(n):
    x = n
    while True:
        y = (n // x + x) // 2
        if x <= y:
            return x
        x = y


'''
isqrt_2 at 10000 iterations: 0.391000032425
Can perform 25575 calls per second.
         30006 function calls in 1.059 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    1.059    1.059 <string>:1(<module>)
        1    0.687    0.687    1.059    1.059 math.py:10(func)
    10000    0.348    0.000    0.372    0.000 math.py:34(isqrt_2)
    10000    0.013    0.000    0.013    0.000 {divmod}
    10000    0.011    0.000    0.011    0.000 {method 'bit_length' of 'long' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {range}
        2    0.000    0.000    0.000    0.000 {time.time}
'''
@benchmark()
def isqrt_2(n):
    if n < 0:
        raise ValueError('Square root is not defined for negative numbers.')
    x = int(n)
    if x == 0:
        return 0
    a, b = divmod(x.bit_length(), 2)
    n = 2 ** (a + b)
    while True:
        y = (n + x // n) >> 1
        if y >= n:
            return n
        n = y


cProfile.run('isqrt_1(10**308)')
cProfile.run('isqrt_2(10**308)')