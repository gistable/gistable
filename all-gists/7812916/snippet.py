#/usr/bin/env python

import lldb

# Put _this_ file into ~/Library/lldb/thread_return.py
# Put the following line into ~/.lldbinit
#     command script import ~/Library/lldb/thread_return.py

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f thread_return.thread_return thread_return')

def thread_return(debugger, command, result, internal_dict):
    '''Prints the return value of the last function you stepped out from.
    
    This is very useful if the return was a complex expression. This lldb command
    prevents you from needing to create a temporary variable just to inspect the return value'''

    # If anyone knows a way of doing this without using needing to script lldb in python...
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    print >> result, str(thread.return_value)
    return lldb.thread.return_value
