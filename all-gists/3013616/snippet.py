import sys, threading, Queue, weakref

try:
    import Tkinter
    _has_tk = True
    _debug_win = None
except ImportError:
    # quietly disable ourselves
    _has_tk = False

class _Watch(Tkinter.Toplevel):
    """a watch window"""
    def __init__(self,watch_id,title):
        self.watch_id, self.view = watch_id, None
        Tkinter.Toplevel.__init__(self,_debug_win.root)
        self.title(title)
        self.protocol("WM_DELETE_WINDOW",self.close)
        self.withdraw()
    def set_view(self,view):
        if self.view:
            self.view.close()
        self.view = view
        if self.view:
            self.deiconify()
        else:
            self.withdraw()
    def close(self):
       _debug_win.watches.pop(self.watch_id,None)
       if self.view:
           self.view.close()
       self.view = None
       self.destroy()
       
class _Watch_Str(Tkinter.Label):
    """a watch object that uses a string representation of the var"""
    def __init__(self,watch,var):
        self.watch, self.var = watch, var
        self.text = Tkinter.StringVar()
        Tkinter.Label.__init__(self,watch,textvariable=self.text,padx=5,pady=5)
        self.update()
    def close(self):
        self.var = None
        self.destroy()
    def update(self):
        if self.var is None:
            return
        var = self.var()
        if var is None:
            self.watch.close()
            return
        var = str(var)
        if var != self.text.get():
            self.text.set(var)
            self.pack()
        _debug_win.root.after(100,self.update)    

class _DebugWin(threading.Thread):
    """the main debugwin thread runs all the Tkinter widget windows; uses a command queue"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()
        self.daemon = True
        self.watches = {}
        self.watch_seq = 0
        self.start()
    def run(self):
        self.root = Tkinter.Tk()
        self.root.withdraw() # don't show
        self.do_update()
        self.root.mainloop()
    def do_watch(self,watch_id,cls,var,title):
        watch = self.watches.get(watch_id)
        if not watch:
            watch = self.watches[watch_id] = _Watch(watch_id,title)
        watch.set_view(cls(watch,var))
    def do_unwatch(self,watch_id):
        watch = self.watches.pop(watch_id,None)
        if watch is not None:
            watch.close()
    def do_update(self):
        try:
            args = self.queue.get_nowait()
            cmd, args = args[0], args[1:]
            cmd(*args)
        except Queue.Empty:
            pass
        self.root.after(100,self.do_update)
    def watch(self,var,title,cls,watch_id):
        if watch_id is None:
            while True:
                watch_id = self.watch_seq
                self.watch_seq += 1
                if watch_id not in self.watches:
                    break
        try:
            v = weakref.ref(var)
        except TypeError:
            v = lambda: var
        self.queue.put((self.do_watch,watch_id,cls,v,title))
        return watch_id
    def unwatch(self,watch_id):
        self.queue.put((self.do_unwatch,watch_id))

def _hook(fn): # decorator for functions that use the debugwin
    if not _has_tk:
        def empty(*args,**kwargs): pass
        return empty
    def wrap(*args,**kwargs):
        global _debug_win
        if not _debug_win: _debug_win = _DebugWin()
        return fn(*args,**kwargs)
    return wrap

@_hook
def watch(var,title="watch"):
    """opens a watch-window on a variable; returns an ID for this window if you want to re-watch or close it"""
    return _debug_win.watch(var,title,_Watch_Str,None)
    
@_hook
def rewatch(watch_id,var,title="watch"):
    """changes what an existing watch-window is looking at; creates watch if a watch with this ID is not open"""
    return _debug_win.watch(var,title,_Watch_Str,watch_id)
    
@_hook
def unwatch(watch_id):
    """closes a watch window if its open"""
    return _debug_win.unwatch(watch_id)

if __name__=="__main__":
    # just an example"
    import time, numpy
    print "watching a numpy 2D array, twice"
    var = numpy.arange(100).reshape((10,10))
    watch(var,"watch 1")
    watch_id = watch(var,"watch 2")
    time.sleep(3)
    print "setting the middle to be 100"
    var[5,5] = 100
    time.sleep(3)
    print "update one watch to something else"
    rewatch(watch_id,"this is something else")
    time.sleep(3)
    print "closing one of the watches explicitly"
    unwatch(watch_id)
    time.sleep(3)
    print "deleting the numpy array; weakref should close watch-window"
    del var
    time.sleep(3)
    print "good-bye!"