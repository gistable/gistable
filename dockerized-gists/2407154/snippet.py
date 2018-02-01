#!/usr/bin/env python
# liuw
# Nasty hack to raise exception for other threads

import ctypes # Calm down, this has become standard library since 2.5
import threading
import time

NULL = 0

def ctype_async_raise(thread_obj, exception):
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        raise ValueError("Invalid thread object")

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, ctypes.py_object(exception))
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, NULL)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    print "Successfully set asynchronized exception for", target_tid

def f():
    try:
        while True:
            time.sleep(1)
    finally:
        print "Exited"

t = threading.Thread(target=f)
t.start()
print "Thread started"
print t.isAlive()
time.sleep(5)
ctype_async_raise(t, SystemExit)
t.join()
print t.isAlive()