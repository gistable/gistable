"""Helper to trace ZODB object registrations in order to debug CSRF false
positives with plone.protect.

This helper is intended for DEBUGGING, not for use in production!
"""

from collections import namedtuple
from functools import partial
from threading import local
from ZODB.utils import u64
import sys
import traceback
import ZODB

# Keep a thread local reference to any original trace function
thread_locals = local()
thread_locals.original_trace_func = None


AnnotatedTraceback = namedtuple(
    'AnnotatedTraceback',
    ['obj', 'oid', 'filename', 'line_no', 'extracted_tb'])


class TraceObjectRegistrations(object):
    """
    Context manager that traces and displays calls to a ZODB
    connection's `register()` method.

    These calls will effectively indicate the first DB write to a persistent
    object, and displaying them for an operation that isn't supposed to cause
    a DB write can help in debugging false positives with plone.protect's
    automatic CSRF protection.

    Once a call to `register()` is intercepted, a message indicating this
    and the corresponding stack trace are displayed.

    :param tb_limit: Maximum depth of the displayed stack trace

    Usage:

    >>> with TraceObjectRegistrations(tb_limit=5):
    ...     something_that_writes_but_shouldnt()

    """

    def __init__(self, tb_limit=10):
        self.tb_limit = tb_limit

    def __enter__(self):
        trace_func = partial(_trace_obj_registration_calls, self.tb_limit)
        set_trace(trace_func)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        remove_trace()


def set_trace(trace_func):
    """Registers a call trace function which will be called for every
    function call, and keeps a reference to any previously set trace function
    in order to be able to restore it.
    """
    global thread_locals

    thread_locals.original_trace_func = sys.gettrace()
    sys.settrace(trace_func)


def remove_trace():
    """Restores the original trace function (if there was one).
    """
    global thread_locals

    sys.settrace(thread_locals.original_trace_func)


def _trace_obj_registration_calls(tb_limit, frame, event, arg):
    """Call trace function to intercept any calls to a ZODB
    connection's .register() method (which effectively indicates a DB write).

    (This function needs to be partially applied first in order to have the
    proper 3 argument signature to be used as a trace function)
    """
    if event != 'call':
        return

    co = frame.f_code
    func_name = co.co_name

    # We only want to trace calls to .register() on a
    # ZODB.Connection.Connection or any of its subclasses.

    if func_name != 'register':
        return

    frame_self = frame.f_locals.get('self')
    if frame_self is None:
        return

    if not issubclass(frame_self.__class__, ZODB.Connection.Connection):
        return

    # At this point we can be reasonably certain that we're in
    # `register(self, obj)` - so we try to get a reference to the object
    # that's being registered to print a more helpful message
    obj = frame.f_locals.get('obj')
    oid = hex(u64(obj._p_oid))

    # Walk up the stack one frame, in order to get the stack frame that's
    # causing the call to `register()`, and build the traceback for that frame
    outer_frame = frame.f_back

    filename = outer_frame.f_code.co_filename
    line_no = outer_frame.f_lineno
    extracted_tb = traceback.extract_stack(outer_frame, limit=tb_limit)

    annotated_tb = AnnotatedTraceback(
        obj, oid, filename, line_no, extracted_tb)

    _display_intercepted_call(annotated_tb)


def _display_intercepted_call(annotated_tb):
    msg = 'DB write to {obj} ({oid}) from "{filename}", line {line_no}'
    msg = msg.format(**annotated_tb._asdict())
    print "=" * len(msg)
    print msg
    print "=" * len(msg)
    print ''.join(traceback.format_list(annotated_tb.extracted_tb))
