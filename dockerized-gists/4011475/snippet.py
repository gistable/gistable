import sys
import functools

'''
Usage:
consider following functions
import stack_trace
def foo():
    pass
def bar():
    foo()
    return 0
def error():
    1/0
def recur(i):
    if i == 0:
        return
    recur(i-1)
@stack_trace.stack_trace(with_return=True, with_exception=True, max_depth=3)
def test():
    bar()
    recur(5)
    error()
test()

The result of executing test():
test    [call]  in test.py line:18
  bar   [call]  in test.py line:6
    foo [call]  in test.py line:3
    foo [return]        None    in test.py line:4
  bar   [return]        0       in test.py line:8
  recur [call]  in test.py line:13
    recur       [call]  in test.py line:13
      recur     [call]  in test.py line:13
      recur     [return]        None    in test.py line:16
    recur       [return]        None    in test.py line:16
  recur [return]        None    in test.py line:16
  error [call]  in test.py line:10
  error [exception]     <type 'exceptions.ZeroDivisionError'>   in test.py line:11
  error [return]        None    in test.py line:11
test    [exception]     <type 'exceptions.ZeroDivisionError'>   in test.py line:22
test    [return]        None    in test.py line:22
'''

class StackTrace(object):
    def __init__(self, with_call=True, with_return=False,
                       with_exception=False, max_depth=-1):
        self._frame_dict = {}
        self._options = set()
        self._max_depth = max_depth
        if with_call: self._options.add('call')
        if with_return: self._options.add('return')
        if with_exception: self._options.add('exception')

    def __call__(self, frame, event, arg):
        ret = []
        if event == 'call':
            back_frame = frame.f_back
            if back_frame in self._frame_dict:
                self._frame_dict[frame] = self._frame_dict[back_frame] + 1
            else:
                self._frame_dict[frame] = 0

        depth = self._frame_dict[frame]

        if event in self._options\
          and (self._max_depth<0\
               or depth <= self._max_depth):
            ret.append(frame.f_code.co_name)
            ret.append('[%s]'%event)
            if event == 'return':
                ret.append(arg)
            elif event == 'exception':
                ret.append(repr(arg[0]))
            ret.append('in %s line:%s'%(frame.f_code.co_filename, frame.f_lineno))
        if ret:
            print("%s%s"%('  '*depth, '\t'.join([str(i) for i in ret])))

        return self

def stack_trace(**kw):
    def entangle(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            st = StackTrace(**kw)
            sys.settrace(st)
            try:
                return func(*args, **kwargs)
            finally:
                sys.settrace(None)
        return wrapper
    return entangle