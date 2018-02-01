"""
We want to run a function asychronously and run a
callback function with multiple parameters when it
returns!

In this example, we are pretending we're analyzing
the names and ages of some people. We want to print
out:

jack 0
jill 1
james 2
"""

import time
from multiprocessing.dummy import Pool
pool = Pool(processes=1)

def async_function(name):
    """
    Function we want to run asynchronously and in parallel,
    usually one with heavy input/output, though using a
    dummy function here.
    """
    time.sleep(1)
    return name
    
def callback_function(name, age):
    """
    Function we want to run with the result of the async
    function. The async function returns one parameter, but
    this function takes two parameters. We have to figure
    out how to pass the age parameter from the async function
    to this function..
    """
    print name, age

for age, name in enumerate(['jack', 'jill', 'james']):
    """
    The async function returns a name to callback_function
    so we don't need to pass that, but we somehow need
    to pass the age parameter to callback_function. One
    way to try to do this which works in JavaScript is
    to use an anonymous function in the loop like this:
    """
    new_callback_function = \
        lambda new_name: callback_function(new_name, age)
    pool.apply_async(
        async_function,
        args=[name],
        callback=new_callback_function
    )

"""
However, this outputs:

    jack 2
    jill 2
    james 2

Notice the age we're printing out is always 2, not 0,1,2
as it should be. This is because 2 is the last item in
the loop. The loop completes before the async functions
can return and the changing loop variable is not getting
passed to the callback.

We can fix this, though, using partial!
"""

from functools import partial
for age, name in enumerate(['jack', 'jill', 'james']):
    """
    Partial is a technique for creating a function that
    just calls another function but with one or more of
    the parameters "frozen". In this way, we can capture
    the 'age' paramter in each iteration of the loop and
    pass it along with the return value of the async
    function.
    """
    new_callback_function = partial(callback_function, age=age)
    pool.apply_async(
        async_function,
        args=[name],
        callback=new_callback_function
    )

pool.close()
pool.join()

"""
Hooray!
"""