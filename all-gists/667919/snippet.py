from twisted.internet import defer, reactor
from twisted.enterprise import adbapi

def deferredInit(deferredName):
    """
    Mark a method as waiting on deferred initialization.
    """
    def _deferredInit(func):
        def __deferredInit(self, *args, **kwargs):
            initDeferred = None
            if(hasattr(self, deferredName)):
                initDeferred = getattr(self, deferredName)
                if(initDeferred.called):
                    return defer.maybeDeferred(func, self, *args, **kwargs)
            else:
                raise RuntimeError("%s doesn't define the Deferred attribute `%s`." % (self.__class__.__name__, deferredName))
            
            def _finish(result):
                return func(self, *args, **kwargs)
            
            def _finish_error(failure):
                print '_finish_err: %s' % failure
            
            resultDeferred = defer.Deferred()
            resultDeferred.addCallbacks(_finish, _finish_error)
            
            initDeferred.chainDeferred(resultDeferred)
            
            return resultDeferred
        return __deferredInit
    
    # if it's a callable, that means there's no arguments
    # so we use the defaultname for the instance's deferred
    if(callable(deferredName)):
        func = deferredName
        deferredName = 'initDeferred'
        return _deferredInit(func)
    
    return _deferredInit

class TestDeferredInit(object):
    def __init__(self):
        self.pool = adbapi.ConnectionPool("MySQLdb", 'localhost', 'modu', 'modu')
        self.initDeferred = self.pool.runQuery("SELECT 'it worked';")
        def _finish_init(msg):
            self.msg = msg
        def _finish_init_error(failure):
            print '_finish_init_err: %s' % failure
        self.initDeferred.addCallbacks(_finish_init, _finish_init_error)
    
    # # this is the same as
    # @deferredInit('initDeferred')
    @deferredInit
    def query(self):
        """
        This method will always return a deferred.
        
        The result will only fire once the Deferred created
        by the deferredInit decorator has fired.
        """
        return self.msg

if(__name__ == '__main__'):
    def _print(msg, label):
        print '%s: %s' % (label, msg)
        # once we've done the third call, quit the reactor
        if(label == '3'):
            reactor.stop()
    
    def _print_error(failure):
        print '_print_err: %s' % failure
    
    test = TestDeferredInit()
    
    # the following calls will not fire until
    # the deferred created by the constructor fires
    
    d = test.query()
    d.addCallbacks(_print, _print_error, callbackArgs=['1'])
    
    d2 = test.query()
    d2.addCallbacks(_print, _print_error, callbackArgs=['2'])
    
    d3 = test.query()
    d3.addCallbacks(_print, _print_error, callbackArgs=['3'])
    
    reactor.run()