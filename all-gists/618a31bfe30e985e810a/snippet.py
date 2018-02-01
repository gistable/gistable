#############################################################################
# Apply a function to a list
#############################################################################

# Instead of...
newlist = []
for word in oldlist:
    newlist.append(word.upper())

# ... use map
newlist = map(str.upper, oldlist)

# Why ?
# - One easy to read line line (instead of 3)
# - Faster: Map to push the loop from the interpreter into compiled C code

#############################################################################
# Loop of integer
#############################################################################

# Instead of...
for i in range(1000):
    print(i)

# ... use xrange 
for i in xrange(1000):
    print(i)

# Why ?
# - Memory: xrange do not create a list. Just an iterator
# - Python 3: xrange replaces range

#############################################################################
# Use genrators (yield) instead of list comprehensions
#############################################################################

# Instead of...
def foo(a, b):
    res = []
    for x in a:
        for y in b:
            if x == y:
                res.append((x, y))
    return res

# ... use yield
def foo(a, b):
    for x in a:
        for y in b:
            if x == y:
                yield(x, y)

# Why ?
# - Save memory if a and/or b are realy big

#############################################################################
# Avoid loop (if possible)
#############################################################################

# Instead of...
def foo(a, b):
    for x in a:
        for y in b:
            if x == y:
                yield (x,y)

# ... use set and union 
def foo(a, b):
    return set(a) & set(b)

# Why ?
# - it is faster...

#############################################################################
# Use Numpy broadcasting approch as often as possible
#############################################################################

# Instead of...
def foo(x):
    m = x.shape[0]
    n = x.shape[1]
    res = np.empty((m, n), dtype=np.float)
    for i in xrange(m):
        for j in xrange(n):
            d = 0.0
            for k in xrange(n):
                tmp = x[i, k] - x[j, k]
                d += tmp * tmp
            res[i, j] = np.sqrt(d)
    return res

# ... use boradcasting
def foo(x):
    return np.sqrt(((x[:, None, :] - x) ** 2).sum(-1))

# Why ?
# - it is (more or less 100 *) faster !!!

#############################################################################
# List [] versus tuple ()
#############################################################################

# Create a tuple...
#   python -m timeit "x=(1,2,3,4,5,6,7,8)"
#   100000000 loops, best of 3: 0.0173 usec per loop
# ...is faster than create a list
#   python -m timeit "x=[1,2,3,4,5,6,7,8]"
#   10000000 loops, best of 3: 0.114 usec per loop

# BUT, access to a tuple...
#   python -m timeit -s "x=(1,2,3,4,5,6,7,8)" "y=x[3]"
#   10000000 loops, best of 3: 0.0387 usec per loop
# ...is slower than access to a list
#   python -m timeit -s "x=[1,2,3,4,5,6,7,8]" "y=x[3]"
#   10000000 loops, best of 3: 0.0284 usec per loop

# and remember that:
# - a tuple is of fixed size while a list is not
# - a tuple takes less space in memory than a list 

#############################################################################
# Lots of class instance ? How to optimize the memory using __slots__
#############################################################################

class LotsOfInstances(object)
    var1 = None
    var2 = None
    var3 = None
    #...
    
    __slots__ = ('var1', 'var2', 'var3')
    
    def __init__(self):
        pass
    
    def method1(self):
        pass

# Why ?
# - Optimize memory:  __slots__ reserves space for the declared variables 
#   and prevents the automatic creation of __dict__ and __weakref__ for each instance.
