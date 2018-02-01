"""
Compare speed of a cython wrapper vs a cffi wrapper to the same underlying
C-code with a fast function and a longer-running function.

This should run anywhere that has cffi and cython installed.

Ouput on my machine with python2.7:


brentp@liefless:/tmp$ python compare-wrappers.py
times for 1 million calls

adding 2 numbers with cffi wrapper:
0.147660017014
adding 2 numbers with cython wrapper:
0.0891411304474
summing numbers between 1 and 2000 with cffi wrapper:
1.6725051403
summing numbers between 1 and 2000 with cython wrapper:
1.54648685455


So Cython is twice as fast for a C-function that returns pretty much instantly.
That difference is nullified (so to speak) when the C function takes more time to run.

Time with pypy:

times for 1 million calls
adding 2 numbers with cffi wrapper:
0.0336790084839
summing numbers between 1 and 2000 with cffi wrapper:
1.42473888397
"""


from timeit import timeit
import cffi
import re
import os.path as op
import sys

PYPY = "pypy_version_info" in dir(sys)


ffi = cffi.FFI()
ffi.cdef("""
int sum(int, int);
long sum_between(int, int);
""")



# here is the C code that we are wrapping. One quick running function and
# another potentially long-running function.
code = """
int sum(int a, int b){
    return a + b;
}

long sum_between(int a, int b){
   long sum = 0;    
   int i;
   for(i=a; i<=b; i++) sum += i;
   return sum;
}
"""
C = ffi.verify(code)

if not PYPY:

    import pyximport; pyximport.install()
    with open('ccy.h', 'w') as fh:
        fh.write(code)

    # for cython, we also need to write the python callable wrappers.
    cycode = """
cdef extern from "%s/ccy.h":
    int sum(int a, int b)
    long sum_between(int a, int b)

cpdef int pysum(int a, int b):
    return sum(a, b)

cpdef long pysum_between(int a, int b):
    return sum_between(a, b)
    """ % op.abspath(".")

    with open('ccy.pyx', 'w') as fh:
        fh.write(cycode)


    import ccy



print "times for 1 million calls"
print "adding 2 numbers with cffi wrapper:"
print timeit("C.sum(55, 55)", setup="from __main__ import C", number=int(1e6))

if not PYPY:
    print "adding 2 numbers with cython wrapper:"
    print timeit("ccy.pysum(55, 55)", setup="from __main__ import ccy")

print "summing numbers between 1 and 2000 with cffi wrapper:"
print timeit("C.sum_between(1, 2000)", setup="from __main__ import C")

if not PYPY:
    print "summing numbers between 1 and 2000 with cython wrapper:"
    print timeit("ccy.pysum_between(1, 2000)", setup="from __main__ import ccy")