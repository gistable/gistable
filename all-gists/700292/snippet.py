# "Understanding Python's closures".
#
# Tested in Python 3.1.2
#
# General points:
#
#    1. Closured lexical environments are stored
#       in the property __closure__ of a function
#
#    2. If a function does not use free variables
#       it doesn't form a closure
#
#    3. However, if there is another inner level
#       which uses free variables -- *all* previous
#       levels save the lexical environment
#
#    4. Property __closure__ of *global* functions
#       is None, since a global function may
#       refer global variables (which are also free
#       in this case for the function) via "globals()"
#
#    5. By default, if there is an *assignment* to the
#       identifier with the same name as a closured one,
#       Python creates a *local variable*, but not modifies
#       the closured one. To avoid it, use `nonlocal` directive,
#       specifying explicitly that the variable is free (closured).
#       (Thanks to @joseanpg). See also http://www.python.org/dev/peps/pep-3104/
#
#
# by Dmitry A. Soshnikov <dmitry.soshnikov@gmail.com>
#
# (C) 2010 Mit Style License

# Define a function
def foo(x):
    # inner function "bar"
    def bar(y):
        q = 10
        # inner function "baz"
        def baz(z):
            print("Locals: ", locals())
            print("Vars: ", vars())
            return x + y + q + z
        return baz
    return bar

# Locals: {'y': 20, 'x': 10, 'z': 30, 'q': 10}
# Vars: {'y': 20, 'x': 10, 'z': 30, 'q': 10}
print(foo(10)(20)(30)) # 70

# Explanation:

# ------ 1. Magic property "__closure__" ----------------------------

# All `free variables` (i.e. variables which are
# neither local vars, nor arguments) of "baz" funtion
# are saved in the internal "__closure__" property.
# Every function has this property, though, not every
# saves the content there (if not use free variables).

# Lexical environment (closure) cells of "foo":
# ("foo" doesn't use free variables, and moreover,
# it's a global function, so its __closure__ is None)
print(foo.__closure__) # None

# "bar" is returned
bar = foo(10)

# Closure cells of "bar":
# (
#     <cell at 0x014E7430: int object at 0x1E1FEDF8>, "x": 10
# )
print(bar.__closure__)

# "baz" is returned
baz = bar(20)

#
# Closure cells of "bar":
# (
#     <cell at 0x013F7490: int object at 0x1E1FEE98>, "x": 10
#     <cell at 0x013F7450: int object at 0x1E1FEDF8>, "y": 20
#     <cell at 0x013F74B0: int object at 0x1E1FEDF8>, "q": 10
# )
#
print(baz.__closure__)

# So, we see that a "__closure__" property is a tuple
# (immutable list/array) of closure *cells*; we may refer them
# and their contents explicitly -- a cell has property "cell_contents"

print(baz.__closure__[0]) # <cell at 0x013F7490: int object at 0x1E1FEE98>
print(baz.__closure__[0].cell_contents) # 10 -- this is our closured "x"

# the same for "y" and "q"
print(baz.__closure__[1].cell_contents) # "y": 20
print(baz.__closure__[2].cell_contents) # "q": 10

# Then, when "baz" is activated it's own environment
# frame is created (which contains local variable "z")
# and merged with property __closure__. The result dictionary
# we may refer it via "locals()" or "vars()" funtions.
# Being able to refer all saved (closured) free variables,
# we get correct result -- 70:
baz(30) # 70

# ------ 2. Function without free variables does not closure --------

# Let's show that if a function doesn't use free variables
# it doesn't save lexical environment vars
def f1(x):
    def f2():
        pass
    return f2

# create "f2"
f2 = f1(10)

# its __closure__ is empty
print(f2.__closure__) # None

# ------ 3. A closure is formed if there's most inner function -------

# However, if we have another inner level,
# then both functions save __closure__, even
# if some parent level doesn't use free vars

def f1(x):
    def f2(): # doesn't use free vars
        def f3(): # but "f3" does
            return x
        return f3
    return f2

# create "f2"
f2 = f1(200)

# it has (and should have) __closure__
print(f2.__closure__) # (<cell at 0x014B7990: int object at 0x1E1FF9D8>,)
print(f2.__closure__[0].cell_contents) # "x": 200

# create "f3"
f3 = f2()

# it also has __closure__ (the same as "f2")
print(f3.__closure__) # (<cell at 0x014B7990: int object at 0x1E1FF9D8>,)
print(f3.__closure__[0].cell_contents) # "x": 200
print(f3()) # 200

# ------ 4. Global functions do not closure -------------------------

# Global functions also do not save __closure__
# i.e. its value always None, since may
# refer via globals()
global_var = 100
def global_fn():
    print(globals()["global_var"]) # 100
    print(global_var) # 100

global_fn() # OK, 100
print(global_fn.__closure__) # None

# ------ 5. By default assignment creates a local var. -----------------
# ------ User `nonlocal` to capture the same name closured variable. ---

# Since assignment to an undeclared identifier in Python creates
# a new variable, it's hard to distinguish assignment to a closured
# free variable from the creating of the new local variable. By default
# Python strategy is to *create a new local variable*. To specify, that
# we want to update exactly the closure variable, we should use
# special `nonlocal` directive. However, if a closured variable is of
# an object type (e.g. dict), it's content may be edited without
# specifying `nonlocal` directive.

# "x" is a simple number,
# "y" is a dictionary
def create(x, y):

    # this simplified example uses
    # "getX" / "setX"; only for educational purpose
    # in real code you rather would use real
    # properties (getters/setters)

    # this function uses
    # its own local "x" but not
    # closured from the "create" function
    def setX(newX):
        x = newX # ! create just *local* "x", but not modify closured!
        # and we cannot change it via e.g.
        # child1.__closure__[0] = dx, since tuples are *immutable*

    # and this one already sets
    # the closured one; it may then
    # be read by the "getX" function
    def setReallyX(newX):
        # specify explicitly that "x"
        # is a free (or non-local) variable
        nonlocal x
        # and modify it
        x = newX

    # as mentioned, if we deal with
    # non-primitive type, we may mutate
    # contents of an object without `nonlocal`
    # since objects are passed by-reference (by-sharing)
    # and we modify not the "y" itself (i.e. not *rebound* it),
    # but its content (i.e. *mutate* it)
    def modifyYContent(foo):
        # add/set a new key "foo" to "y"
        y["foo"] = foo

    # getter of the "x"
    def getX():
        return x

    # getter of the "y"
    def getY():
        return y

    # return our messaging
    # dispatch table
    return {
        "setReallyX": setReallyX,
        "setX": setX,
        "modifyYContent": modifyYContent,
        "getX": getX,
        "getY": getY
    }

# create our object
instance = create(10, {})

# "setX" does *not* closure "x" since uses *assignment*!
# it doesn't closuse "y" too, since doesn't use it:
print(instance["setX"].__closure__) # None

# do *not* modify closured "x" but
# just create a local one
instance["setX"](100)

# test with a getter
print(instance["getX"]()) # still 10

# test with a "setReallyX", it closures only "x"
# (
#     <cell at 0x01448AD0: int object at 0x1E1FEDF8>, "x": 10
# )
print(instance["setReallyX"].__closure__)
instance["setReallyX"](100)

# test again with a getter
print(instance["getX"]()) # OK, now 100

# "modifyYContent" captrues only "y":
# (
#     <cell at 0x01448AB0: dict object at 0x0144D4B0> "y": {}
# )
print(instance["modifyYContent"].__closure__)

# we may modify content of the
# closured variable "y"
instance["modifyYContent"](30)

print(instance["getY"]()) # {"foo": 30}