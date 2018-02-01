# Wanted to test the penalty for using imports inside functions.

import timeit

def t1():
    return 2 * 2

timeit.timeit("t1()", setup="from __main__ import t1")

#> 0.14718103408813477

def t2():
    import os
    return 2 * 2

timeit.timeit("t2()", setup="from __main__ import t2")

#> 1.1158959865570068
# Ouch!

def t3():
    os = __import__('os')
    return 2 * 2

timeit.timeit("t3()", setup="from __main__ import t3")

#> 0.7558999061584473

import sys
import os
def t4():
    os = sys.modules.get('os')
    return 2 * 2

timeit.timeit("t4()", setup="from __main__ import t4, os, sys")

#> 0.45201706886291504

import sys
import os

def myimport(module):
    return sys.modules.get(module) or __import__(module)

def t5():
    os = myimport('os')
    return 2 * 2

timeit.timeit("t5()", setup="from __main__ import t5, myimport, os, sys")

#> 0.6421878337860107

# Conclusion: Not for performance critical areas.