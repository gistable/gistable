"""
    multiprocesscallback.py, by Peter Sobot (psobot.com), May 13, 2012
    
    Handles callback functions in classes that have member functions that
    are executed in a different process. A crazy experiment in Python
    magic that breaks a lot of rules.
    
    Do not use in production, for any reason. (Although I do.)
    
    If your class takes in a callback, like so:
    
        class MyClass(object):
            def __init__(self, callback):
            
    you can call MultiprocessCallback.register_all(queue) to auto-create
    member functions with the names of the callback variables, which,
    when called, will be safely executed in the parent process. E.g.:
    
        class MyClass(object):
            def __init__(self, my_callback):
                self._pq = multiprocessing.Queue()
                MultiprocessCallback.register_all(self._pq)
                
            def start_other_process():
                target = MultiprocessCallback.target(self.runs_in_another_process)
                p = multiprocessing.Process(target=target)
                p.start()
                MultiprocessCallback.listen()
                p.join()
            
            def runs_in_another_process():
                self.my_callback("hey look, some data!")
            
    The data in the callback must be picklable, as it will be sent across
    the multiprocess boundary.
    
    The parent process can read from the queue itself and run .execute()
    on the MultiprocessCallback objects, or it can use the *blocking*
    MultiprocessCallback.listen(), which provides a basic listener.
    
    Known bugs or omissions:
        - Will straight-up just not work in Windows.
          (The scenario doesn't exist - you can't use multiprocessing on
           member functions on Windows.)
"""   

import multiprocessing
import traceback
import inspect
import sys
import time

__author__ = "psobot"

class EndListener(Exception): pass

def register_all(queue=None):
    _locals = inspect.getargvalues(sys._getframe(1))[3]
    if not queue:
        queue = multiprocessing.Queue()
        setattr(_locals['self'], "_mpcq", queue)
    for n, v in dict([(_n, _v) for (_n, _v) in _locals.iteritems() if _n != "self"]).iteritems():
        if hasattr(v, "__call__"):
            proc = multiprocessing.current_process().name
            setattr(_locals['self'], n, lambda *args, **kwargs: _safecall(proc, queue, n, v, *args, **kwargs))
            
def _safecall(proc, queue, n, _c, *args, **kwargs):
    if multiprocessing.current_process().name != proc:
        queue.put(MultiprocessCallback(n, *args, **kwargs))
    else:
        return _c(*args, **kwargs)

def listen(queue=None):
    if not queue:
        _locals = inspect.getargvalues(sys._getframe(1))[3]
        queue = _locals['self'].__dict__["_mpcq"]
    data = queue.get()
    while not isinstance(data, EndListener):
        if isinstance(data, MultiprocessCallback):
            data.execute()
        data = queue.get()

def target(_callable, queue=None):
    def _target(*args, **kwargs):
        _callable(*args, **kwargs)
        end(queue)
    return _target
        
def end(queue=None):
    if not queue:
        i = 1
        _locals = inspect.getargvalues(sys._getframe(i))[3]
        while not 'self' in _locals or not '_mpcq' in _locals['self'].__dict__:
            i += 1
            _locals = inspect.getargvalues(sys._getframe(i))[3]
        queue = _locals['self'].__dict__["_mpcq"]
    queue.put(EndListener())

class MultiprocessCallback(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.stackf = traceback.format_stack(sys._getframe(3), 2)
        self.originator = multiprocessing.current_process().name
        self.args = args
        self.kwargs = kwargs
    
    def execute(self, search=None):
        if not search:
            i = 1
            search = inspect.getargvalues(sys._getframe(i))[3]
            while not self.name in search:
                i += 1
                search = inspect.getargvalues(sys._getframe(i))[3]
                if not self.name in search and 'self' in search:
                    search = search['self'].__dict__
        if self.name in search:
            if hasattr(search[self.name], '__call__'):
                try:
                    r = search[self.name](*self.args, **self.kwargs)
                    if r is not None:
                        print "Warning: return value from callback ignored."
                except Exception, e:
                    e.args = (" ".join(list(e.args) +
                                       ["\nOriginally called from %s (most recent call last):\n" % self.originator] +
                                       self.stackf), )
                    raise
            else:
                raise ValueError("Function %s not callable." % self.name)
        else:
            raise KeyError("Function %s not provided." % self.name)

if __name__ == "__main__":
    class Test(object):   
        def __init__(self, callback = None):
            register_all()
            
        def run_me(self):
            """
                Run self.separate_process in its own process.
                When the callback is called, it will execute in the
                parent process.
            """
            p = multiprocessing.Process(target=target(self.separate_process))
            p.start()
            listen()
            p.join()
        
        def separate_process(self):
            for i in xrange(0, 10):
                #    some intense computation
                self.callback(i)
                time.sleep(0.1)
    
    count = 0
    def my_callback(i):
        """
            Increments a global variable by i in the main process.
        """
        if multiprocessing.current_process().name != "MainProcess":
            raise multiprocessing.ProcessError("The global is being incremented in the wrong process!")
        global count
        count += i
        print "Counter in main process is now: %s" % count
        
    Test(callback=my_callback).run_me()