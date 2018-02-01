import sys
import threading
import Queue

import wx

_noTimeoutDefault = object()
def defer(
    returnToFunction,
    function,
    args=None,
    kwargs=None,
    timeout=None,
    timeoutFunction=None,
    timeoutDefault=_noTimeoutDefault,
    exceptionFunction = None,
):
    if not args:
        args = ()
    if not kwargs:
        kwargs = {}
    resultQueue = Queue.Queue()
    workerThread = WorkerThread(function, args, kwargs, resultQueue)
    monitorThread = MonitorThread(resultQueue, returnToFunction, timeout, 
                                  timeoutFunction, timeoutDefault, 
                                  exceptionFunction)
    workerThread.start()
    monitorThread.start()

def reraise(exception, trace):
    """
    """
    raise exception.__class__, exception, trace
defer.reraise = reraise

class WorkerThread(threading.Thread):
    def __init__(self, function, args, kwargs, resultQueue):
        self.function = function
        self.resultQueue = resultQueue
        self.args = args
        self.kwargs = kwargs
        
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
        except:
            (exception,trace) = sys.exc_info()[1:]
            self.resultQueue.put((False,(exception,trace)))
        else:
            self.resultQueue.put((True,result))

class MonitorThread(threading.Thread):
    def __init__(
        self,
        resultQueue,
        returnToFunction,
        timeout,
        timeoutFunction,
        timeoutDefault,
        exceptionFunction,
    ):
        self.resultQueue = resultQueue
        self.returnToFunction = returnToFunction
        self.timeout = timeout
        self.timeoutFunction = timeoutFunction
        self.timeoutDefault = timeoutDefault
        self.exceptionFunction = exceptionFunction
        
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            (isResult, result) = self.resultQueue.get(True, self.timeout)
            if isResult:
                if self.returnToFunction is not None:
                    wx.CallAfter(self.returnToFunction, result)
            elif self.exceptionFunction:
                (exception,trace) = result
                wx.CallAfter(self.exceptionFunction, exception, trace)
        except Queue.Empty:
            print "****** timeout"
            # We can't externally kill the worker thread. The best we can do is
            # hope it finishes at some point to free resources. Since it is a
            # deamon it won't prevent program termination if it never finishes.
            
            if self.timeoutFunction:
                if self.timeoutDefault == _noTimeoutDefault:
                    wx.CallAfter(self.timeoutFunction)
                else:
                    wx.CallAfter(self.timeoutFunction, self.timeoutDefault)
            else:
                if self.timeoutDefault == _noTimeoutDefault:
                    wx.CallAfter(self.returnToFunction)
                else:
                    wx.CallAfter(self.returnToFunction, self.timeoutDefault)


def test():
    import time
    import random

    timeout = random.choice(xrange(1,5))
    sleep = random.choice(xrange(1,5))
    def slowFunction(wait):
        time.sleep(wait)
        return "slowFunction() managed to finish before timeout"
    
    def resultCallback(result):
        label.SetLabel(result)
    
    def timeoutCallback():
        label.SetLabel('slowFunction() did not finish before timeout')
    
    app = wx.PySimpleApp()
    frame = wx.Frame(None,-1,"defer test with random time")
    
    panel = wx.Panel(frame,-1)
    panelSizer = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(panelSizer)
    
    label = wx.StaticText(panel,-1)
    label.SetLabel('slowFunction() takes %s sec to run, timeout=%s sec' %(sleep, timeout))

    panelSizer.Add(label)

    frame.Show(True)
    
    defer(resultCallback, slowFunction, (sleep,), timeout=timeout, timeoutFunction=timeoutCallback)
    
    app.MainLoop()

if __name__ == '__main__':
    test()
