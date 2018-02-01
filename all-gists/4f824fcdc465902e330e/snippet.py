# Inspired by the following sentence that I ran across this morning:
#
#    "f_lineno is the current line number of the frame - writing to
#     this from within a trace function jumps to the given line
#     (only for the bottom-most frame). A debugger can implement a
#     Jump command (aka Set Next Statement) by writing to f_lineno."
#
#    https://docs.python.org/2/reference/datamodel.html
#
# There is an older implementation of a similar idea:
# the 2004 April Fool's joke at
#
#    http://entrian.com/goto/index.html
#
# But as their implementation is 110+ lines that re-parses the module
# that uses "goto", I had mistakenly believed that they were editing
# the AST or something to implement goto.  Having now re-read their code,
# I see that the parsing is simply to allow forward label references;
# at its core, their logic uses the same f_lineno trick that I am using here.
#
# Oh - I should also note a limitation of this silly experiment, just in
# case it saves time for anyone who plays with it: a goto() is ignored if
# it is the last line of a function, because once a function has completed
# its last line of code the interpreter ignores f_lineno, even if it gets
# pointed back into the body of the function.

import inspect
import sys
from functools import wraps

_python3 = sys.version_info[0] >= 3

def enable_goto(function):
    @wraps(function)
    def wrapper(*args, **kw):
        def trace_call(frame, event, arg):
            return trace_line if (frame.f_code is code) else None
        def trace_line(frame, event, arg):
            if target_list:
                frame.f_lineno = target_list.pop()
        target_list = []
        sys.settrace(trace_call)
        try:
            function(*args, **kw)
        finally:
            sys.settrace(None)
    code = function.__code__ if _python3 else function.func_code
    return wrapper

def goto(target):
    inspect.currentframe().f_back.f_back.f_locals['target_list'].append(target)

def label():
    return inspect.currentframe().f_back.f_lineno + 1

def offset(n):
    return inspect.currentframe().f_back.f_lineno + n

# Goto, without a label:

@enable_goto
def count1():
    i = 0
    print(i)   # this is the line targeted by goto(-3)
    i = i + 1
    if i < 10:
        goto(offset(-3))
    print('done')

count1()

# Goto, with a label:

@enable_goto
def count1():
    i = 0
    top_of_loop = label()
    print(i)
    i = i + 1
    if i < 10:
        goto(top_of_loop)
    print('done')

count1()
