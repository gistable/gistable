import asyncio
import functools
import random

class Message(object):
    
    def __init__(self, message, payload={}):
        self.message = message
        self.payload = payload
        self.result = None
        
    def respond(self, r):
        if self.result:
            self.result.set_result(r)
        
class QueryMessage(Message):
    
    def __init__(self, message, payload={}):
        super().__init__(message, payload)
        self.result = asyncio.Future()
        
class StopMessage(Message):
    
    def __init__(self):
        super().__init__('__STOP__')

class Actor(object):
    
    def __init__(self, **kwargs):
        
        # pull useful configuration params from kwargs
        self._max_inbox_size = kwargs.get('max_inbox_size', 0)
        self._loop = kwargs.get('loop', asyncio.get_event_loop())
        self._raise_unknown_messages = kwargs.get('raise_unknown_messages', False)
        self._delay_start = kwargs.get('delay_start', False)
        
        self._inbox = asyncio.Queue(loop=self._loop, maxsize=self._max_inbox_size)
        self._handlers = {}
        self._is_running = False
        
        # add built-in handlers
        self.register_handler('__STOP__', self._stop_handler)
        
        # start running
        if not self._delay_start:
            self.start()
        
    def register_handler(self, message, func):
        self._handlers[message] = func
        
    def unregister_handler(self, message):
        del(self._handlers[message])
        
    def start(self):
        if not self._is_running:
            self._loop.create_task(self._run())
            self._is_running = True
            
    @asyncio.coroutine  
    def stop(self):
        if self._is_running:
            self._is_running = False
            yield from self._receive(StopMessage())
    
    @asyncio.coroutine  
    def _stop_handler(self, message):
        self._is_running = False
    
    @asyncio.coroutine
    def _run(self):
        while self._is_running:
            message_obj = yield from self._inbox.get()
            try:
                message = message_obj.message
                result = message_obj.result
            except AttributeError:
                print('Could not pull data from message. ' 
                      'Are you sure it\'s a Message object?')
                raise
            if message in self._handlers:
                handler_func = self._handlers[message]
                handler_result = yield from handler_func(message_obj)
                # if the sender is expecting a response
                if result:
                    result.set_result(handler_result)
            elif self._raise_unknown_messages:
                raise KeyError('Message type {0} does not have a handler'.format(message))
    
    @asyncio.coroutine            
    def _receive(self, message):
        yield from self._inbox.put(message)
    
    # Send a message and don't wait for a response.
    @asyncio.coroutine
    def tell(self, target, message):
        yield from target._receive(message)
    
    # Send a message and block until you get a response.
    @asyncio.coroutine    
    def ask(self, target, message):
        try:
            result_handle = message.result
        except AttributeError:
            print('Could not get response future from message. '
                  'Are you sure it\'s a Message object?')
            raise
        if result_handle is None:
            raise ValueError('message.response cannot be none for an ask.')
        
        yield from self.tell(target, message)
        
        # This will block until response_handle is filled
        return (yield from result_handle)   
        
        
        
#########################################
# Example
#########################################        
        

class AnswerActor(Actor):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_handler('question', self.handle_question)
        
    @asyncio.coroutine
    def handle_question(self, message):
        return 42
        
@asyncio.coroutine
def test():
    a = AnswerActor()
    b = Actor()
    r = yield from b.ask(a, QueryMessage('question'))
    print(r)
    yield from a.stop()
    yield from b.stop()
    
asyncio.get_event_loop().run_until_complete(test()) 

# prints 42   