from idaapi import *
from idc import *

def get_stack_arg(arg, base='ebp'):
    # find the stack frame
    stack = GetFrame(here())
    size  = GetStrucSize(stack)

    # figure out all of the variable names
    names = []
    for i in xrange(size):
        n = GetMemberName(stack, i)
        if n and not n in names:
            names.append(n)

    # The stack offsets can be negative
    # GetFrame and GetStrucSize are not
    #-0000000A var_A dw ?
    #+00000000  s db 4 dup(?) ; s is always at 0x0 
    #+00000004  r db 4 dup(?)
    #+00000008 arg_0 dd ?
    #+0000000C arg_4 dd
    # there has got too be a better way (hax)
    if ' s' in names and arg in names:                                                                                                    
        adjusted = size - (size - GetMemberOffset(stack, ' s'))
        
        offset = GetMemberOffset(stack, arg) - adjusted
        if base:
            return GetRegValue(base) + offset
        else:
            return offset

    return -1