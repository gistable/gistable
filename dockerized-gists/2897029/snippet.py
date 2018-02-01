# Trace 'print' statement calls cluttering your test suite output.
#
# It is not that simple to track 'print' statement in Python 2.x - it
# cannot be monkey-patched itself, because it's not a function. So we
# override sys.stdout and check the backtrace when stdout is written
# to.
#
# The overload happens only if TRACE_PRINT environment variable is
# set. By default, only the offending file name and line number is
# printed; if TRACE_PRINT environment variable is set to 'traceback',
# full call stack is printed to find most tricky cases.

import os, sys, traceback

class Proxy(object):
    def __init__(self, target_object):
        self._count = {}
        self._obj = target_object

    def __getattr__(self, attr):
        if attr in self._count: 
            self._count[attr]+=1
        else: 
            self._count[attr]=1
        return getattr(self._obj, attr)

    def write(self, *args, **kwargs):
        rv = self._obj.write(*args, **kwargs)
        for filename, lineno, function, line in traceback.extract_stack():
            if 'print' in line:
                if os.environ.get('TRACE_PRINT', None) == 'traceback':
                    traceback.print_stack()
                else:
                    sys.stderr.write("%s:%d (%s): %s\n" % (filename, lineno, function, line))
                break

if os.environ.get('TRACE_PRINT', None):
    sys.stdout = Proxy(sys.stdout)
