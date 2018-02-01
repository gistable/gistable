
## The MIT License (MIT)
## ---------------------
##
## Copyright (C) 2014 Nicco Kunzmann
##
## https://gist.github.com/niccokunzmann/6038331
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the "Software"),
## to deal in the Software without restriction, including without limitation
## the rights to use, copy, modify, merge, publish, distribute, sublicense,
## and/or sell copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included
## in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
## OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.

"""
copy this code and do

    import hanging_threads

If a thread is at the same place for SECONDS_FROZEN then the stacktrace is printed.

This script prints

--------------------    Thread 6628     --------------------
  File "hanging_threads.py", line 70, in <module>
        time.sleep(3) # TEST
--------------------    Thread 6628     --------------------
  File "hanging_threads.py", line 70, in <module>
        time.sleep(3) # TEST

"""
import sys
import threading
try:
    try:
        from threading import _get_ident as get_ident
    except ImportError:
        from threading import get_ident
except ImportError:
    from thread import get_ident
import linecache
import time

SECONDS_FROZEN = 10 # seconds
TESTS_PER_SECOND = 10

def frame2string(frame):
    # from module traceback
    lineno = frame.f_lineno # or f_lasti
    co = frame.f_code
    filename = co.co_filename
    name = co.co_name
    s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
    line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
    return s + '\n\t' + line

def thread2list(frame):
    l = []
    while frame:
        l.insert(0, frame2string(frame))
        frame = frame.f_back
    return l

def monitor():
    self = get_ident()
    old_threads = {}
    while 1:
        time.sleep(1. / TESTS_PER_SECOND)
        now = time.time()
        then = now - SECONDS_FROZEN
        frames = sys._current_frames()
        new_threads = {}
        for frame_id, frame in frames.items():
            new_threads[frame_id] = thread2list(frame)
        for thread_id, frame_list in new_threads.items():
            if thread_id == self: continue
            if thread_id not in old_threads or \
               frame_list != old_threads[thread_id][0]:
                new_threads[thread_id] = (frame_list, now)
            elif old_threads[thread_id][1] < then:
                print_frame_list(frame_list, frame_id)
            else:
                new_threads[thread_id] = old_threads[thread_id]
        old_threads = new_threads

def print_frame_list(frame_list, frame_id):
    sys.stderr.write('-' * 20 + 
                     'Thread {}'.format(frame_id).center(20) +
                     '-' * 20 +
                     '\n' + 
                     ''.join(frame_list))

def start_monitoring():
    '''After hanging SECONDS_FROZEN the stack trace of the deadlock is printed automatically.'''
    thread = threading.Thread(target = monitor)
    thread.daemon = True
    thread.start()
    return thread

monitoring_thread = start_monitoring()

if __name__ == '__main__':
    SECONDS_FROZEN = 1
    time.sleep(3) # TEST
