# Demo of late binding in Python's closures and how to avoid it when needed

functions = []
for n in [1, 2, 3]:
    def func(x):
        return n*x
    functions.append(func)

# You would expect this to print [2, 4, 6]
print(
    'calling a list of bad closures and output is: {}'
    .format(str([function(2) for function in functions]))
)
# But it will print [6, 6, 6] actually, because Python binds late the n
# variable, after the execution of the for loop above when n equals 3

# To avoid this behavior one of the options you can use is default arguments:
functions = []
for n in [1, 2, 3]:
    def func(x, n=n):
        return n*x
    functions.append(func)

# This will print [2, 4, 6]
print(
    'calling a list of functions with default arguments and output is: {}'
    .format(str([function(2) for function in functions]))
)
# I don't like this solution though as it's rather hacky

# The solution I would use in this case would be to use functools.partial:
from functools import partial

functions = []
for n in [1, 2, 3]:
    def func(n, x):
        return n*x
    functions.append(partial(func, n))

print(
    'calling a list of partialy built functions and output is: {}'
    .format(str([function(2) for function in functions]))
)