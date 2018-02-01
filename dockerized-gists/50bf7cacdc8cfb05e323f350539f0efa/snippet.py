'''
    This is significantly derived from StackContext, Apache 2.0 license
'''

from tornado.stack_context import StackContextInconsistentError, _state

class ContextLocal(object):
    '''
        Implements a threadlocal-like mechanism that can be used to track data
        across tornado asynchronous calls. This is very similar to (and based
        upon) :class:`.StackContext`, and can be used in parallel with
        StackContext.
        
        To use this, you should define a class type that inherits from this
        class, instead of creating a ContextLocal object directly::
        
            class MyLocal(ContextLocal):
                pass
                
            def something_else():
            
                data = MyLocal.current_data()
                assert data['foo'] == 1
                
            def something():
                with MyLocal() as ctx:
                    ctx.data['foo'] = 1
                    
                    .. 
                    
                    IOLoop.current().add_callback(something_else)
        
        You can also nest ContextLocal blocks, and it will return the last
        context of the correct type::
        
            class MyLocal(ContextLocal):
                pass
                
            class MyOtherLocal(ContextLocal):
                pass
            
            def something_else():
                with MyOtherLocal() as other_ctx:
                    local = MyLocal.current()
                    # this is the original mylocal instance
        
            def something():
                with MyLocal() as ctx:
                    something_else()
                    
                    
        Like StackContext, you can use IOLoop.spawn_callback to signify a
        completely new context, and ContextLocal.current() will be cleared
        in that context::
        
            class MyLocal(ContextLocal):
                pass
                
            def spawned():
                assert MyLocal.current() is None
                
            def something()
                with MyLocal() as ctx:
                    IOLoop.current().spawn_context(spawned)
        
    '''
    
    def __init__(self, data=None):
        '''
            :param data: Set to the default object to store in the context
                         or it will be initialized to be {}
        '''
        if data is None:
            data = {}

        self.active = True
        self.data = data

    def enter(self):
        # unused
        pass

    def exit(self, type, value, traceback):
        # unused
        pass
    
    def __enter__(self):
        self.old_contexts = _state.contexts
        self.new_contexts = (self.old_contexts[0] + (self,), self)
        _state.contexts = self.new_contexts

        return self

    def __exit__(self, type, value, traceback):
        final_contexts = _state.contexts
        _state.contexts = self.old_contexts

        if final_contexts is not self.new_contexts:
            raise StackContextInconsistentError(
                'stack_context inconsistency (may be caused by yield '
                'within a "with StackContext" block)')

        # Break up a reference to itself to allow for faster GC on CPython.
        self.new_contexts = None

    def deactivate(self):
        self.active = False

    @classmethod
    def current(cls):
        '''
            :returns: current context instance or None
        '''
        for ctx in reversed(_state.contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx
    
    @classmethod
    def current_data(cls):
        '''
            :returns: current context data or None 
        '''
        for ctx in reversed(_state.contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx.data

    def prev_ctx(self):
        '''
            Walks up the list of contexts to find another one of this type
            
            .. note:: The 'top' of the context stack is where a NullContext
                      was used, so this cannot walk past a NullContext
        '''
        cls = self.__class__
        for ctx in reversed(self.old_contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx


if __name__ == '__main__':

    from tornado.ioloop import IOLoop
    from tornado.gen import multi, Future
    
    io_loop = IOLoop.current()

    class MyLocal(ContextLocal):
        pass

    class MyOtherLocal(ContextLocal):
        pass

    def _cb(f):
        with MyOtherLocal() as ctx:
            ctx.data['foo'] = 2

            # this is the original mylocal instance
            assert MyLocal.current() is not None
            assert MyLocal.current_data()['foo'] == 1

        assert MyOtherLocal.current() == None
        f.set_result(True)

        print("_cb")

    def _spawned_cb(f):
        assert MyLocal.current() == None
        f.set_result(True)

        print("_spawned_cb")

    def _main():
        
        f1 = Future()
        f2 = Future()
        
        with MyLocal() as ctx:
            ctx.data['foo'] = 1

            io_loop.add_callback(_cb, f1)
            io_loop.spawn_callback(_spawned_cb, f2)
            
        with MyLocal() as ctx1:
            with MyLocal() as ctx2:
                assert ctx2.prev_ctx() == ctx1

        return multi([f1, f2])

    io_loop.run_sync(_main)
    print("Success")

