# Define
def singledispatch(func):
    through_map = {}
    def register(through):
        def _on(what):
            through_map[through] = what
            return what
        return _on

    def dispatch(what):
        return through_map.get(what, func)

    def run(arg):
        return through_map.get(type(arg), func)(arg)

    run.register = register 
    run.dispatch = dispatch
    return run
            
# Use
@singledispatch
def fun(arg):
    return 'generic: {}'.format(arg)

@fun.register(str)
def _str(arg):
    return 'str: {}'.format(arg)

@fun.register(int)
def _int(arg):
    return 'int: {}'.format(arg)

@fun.register(float)
def _(arg):
    return 'float: {}'.format(arg)

# Test
assert fun(1) == 'int: 1'
assert fun(1.0) == 'float: 1.0'
assert fun('omar') == 'str: omar'
assert fun([1,2,3]) == 'generic: [1, 2, 3]'
assert fun.dispatch(int) == _int
