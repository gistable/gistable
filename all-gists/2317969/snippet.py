import inspect

def marmoset_patch(func, s, r):
    source = inspect.getsource(func).replace(s, r)
    exec source in func.func_globals
    func.func_code = func.func_globals[func.__name__].func_code

def foo():
    print 1
    print 2
    print 3

foo()
# 1
# 2
# 3

marmoset_patch(foo, '3', "'ZOMG'")
foo()
# 1
# 2
# ZOMG
