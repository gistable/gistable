# There are many patterns in python where a decorator is used to add a function to a registry,
# without altering it at all. Often, the function doesn't need to exist outside of the registry,
# and a minimal def is supplied- just enough to be decorated. The functools.singledispatch
# decorator is an example of this:

@singledispatch
def func(arg):
    print(arg)


@func.register(int)
def _(arg):
    print("arg is an int:", arg)

# What I'm proposing is a syntax that would make this pattern have slightly less boilerplate. It
# looks like this:

@func.register(list)(arg):
    print("arg is a list:", arg)

# To be clear, this syntax ONLY applies to decorators. If the trailing colon is present, the last
# parenthesised group is interpreted as an argument list, and used to create an anynomous function,
# which is sent to the decorator. The decorator returns as normal, so decorators can still be
# nested. However, the final return value is discarded:

@func.register(dict)
@some_other_decorator
def _(arg):
    print("arg is a dict:", arg)


@func.register(tuple)
@some_other_decorator(arg):
    print("arg is a tuple:", arg)

# Finally, if NO parenthesized groups are present, the anynomous function is created with no parameters.
# The following 2 examples are equivelent, except that no function called _ is created in the latter
# case:

@some_other_decorator
def _():
    print("I was decorated!")


@some_other_decorator:
    print("I was decorated!")

# All feedback is welcome.