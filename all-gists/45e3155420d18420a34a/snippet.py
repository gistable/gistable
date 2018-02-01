# http://www.artima.com/weblogs/viewpost.jsp?thread=101605

@multimethod(int, int)
def foo(a, b):
    return a + b 
@multimethod(float, float):
def foo(a, b):
    return int(a+b)
@multimethod(str, str):
def foo(a, b):
    return '{} + {}'.format(a,b)
    
# http://blog.chadselph.com/adding-functional-style-pattern-matching-to-python.html

@ifmatches
def foo(a=OfType(int), b=fType(int):
    return a + b 
@ifmatches
def foo(a=OfType(float), b=fType(flaot):
    return int(a+b)
@ifmatches
def foo(a=OfType(str), b=fType(str):
    return '{} + {}'.format(a,b)
    
# Also see: http://svn.colorstudy.com/home/ianb/recipes/patmatch.py





