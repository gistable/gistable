import gevent
import gevent.pool

class GroupWithExceptionCatching(gevent.pool.Group):
    def __init__(self, *args):
        super(GroupWithExceptionCatching, self).__init__(*args)
        self._error_handlers = {}
    
    def _wrap_errors(self, func):
        """Wrap a callable for triggering error handlers
        
        This is used by the greenlet spawn methods so you can handle known
        exception cases instead of gevent's default behavior of just printing
        a stack trace for exceptions running in parallel greenlets.
        
        """
        def wrapped_f(*args, **kwargs):
            exceptions = tuple(self._error_handlers.keys())
            try:
                return func(*args, **kwargs)
            except exceptions, exception:
                for type in self._error_handlers:
                    if isinstance(exception, type):
                        handler, greenlet = self._error_handlers[type]
                        self._wrap_errors(handler)(exception, greenlet)
                return exception
        return wrapped_f
    
    def catch(self, type, handler):
        """Set an error handler for exceptions of `type` raised in greenlets"""
        self._error_handlers[type] = (handler, gevent.getcurrent())
    
    def spawn(self, func, *args, **kwargs):
        parent = super(GroupWithExceptionCatching, self)
        func_wrap = self._wrap_errors(func)
        return parent.spawn(func_wrap, *args, **kwargs)
    
    def spawn_later(self, seconds, func, *args, **kwargs):
        parent = super(GroupWithExceptionCatching, self)
        func_wrap = self._wrap_errors(func)
        return parent.spawn_later(seconds, func_wrap, *args, **kwargs)

if __name__ == '__main__':
    class MyException(Exception): pass
    
    def raise_uncaught_exception():
        raise Exception("This will be uncaught")
    
    def raise_exception_to_catch():
        raise MyException("This will be nicely printed")
    
    group = GroupWithExceptionCatching()
    group.spawn(raise_uncaught_exception) # will result in stack trace!
    
    def handle_error(error, greenlet):
        print error
    group.catch(MyException, handle_error)
    group.spawn(raise_exception_to_catch)
    
    group.join()
    
    # You can also now raise the exception in the greenlet that
    # set the exception handler (great for testing)
    
    def raise_in_handling_greenlet(error, greenlet):
        greenlet.throw(error)
    
    try:
        group = GroupWithExceptionCatching()
        group.catch(MyException, raise_in_handling_greenlet)
        group.spawn(raise_exception_to_catch)
        group.join()
    except MyException:
        print "Caught it in the main greenlet"