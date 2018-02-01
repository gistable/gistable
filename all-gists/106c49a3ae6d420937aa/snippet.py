# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from functools import wraps

class Exception_StopQThread(Exception):
    pass

class Runnable(QtCore.QRunnable):
    def __init__(self, func, args, kwargs):
        QtCore.QRunnable.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception_StopQThread:
            #Return using stop function
            pass
        except:
            #TODO: send the exception to debug
            pass

pool = QtCore.QThreadPool()
pool.setMaxThreadCount(1) #serial execution

def AsQThread(func):
    """
    Decorator to execute a func inside the QThreadPool
    """
    @wraps(func)
    def AsyncFunc(*args, **kwargs):
        runnable = Runnable(func = func, args = args, kwargs = kwargs)
        global pool
        pool.start(runnable)
        
    return AsyncFunc
    
_STOP = False

def check_stop():
    global _STOP
    if _STOP == True:
        raise Exception_StopQThread()

def stop():
    global _STOP
    global pool
    _STOP = True
    pool.waitForDone()
    _STOP = False

class SignalCaller(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    def __init__(self, func, args = (), kwargs = {}):
        QtCore.QObject.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signal.connect(self.main)
    def main(self):
        self.func(*self.args, **self.kwargs)
    def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.signal.emit()
        
def GUI_Safe(func):
    """
    Decorator to execute func into the GUI thread
    """
    S = SignalCaller(func)
    return S.run
    
#Test code for Ipython
#%pylab qt
#import time
#import QThreadDecorators as QTh
#
#x = arange(20)
#y = x * nan
#
#@QTh.GUI_Safe
#def myplot():
#    plot(x, y, 'bo-')
#
#@QTh.AsQThread
#def myLoop():
#    for i, xi in enumerate(x):
#        y[i] = xi**2
#        myplot()
#        time.sleep(1)
#        QTh.check_stop()
#
#myLoop()
##Wait some time...
#QTh.stop()