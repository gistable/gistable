import eventlet
eventlet.monkey_patch()
from eventlet.green import zmq
from eventlet.event import Event

import inspect, time
from marshal import dumps, loads
from time import time as unixtime

# http://anthon.home.xs4all.nl/Python/ordereddict/
try:
    from _ordereddict import ordereddict as OrderedDict
except ImportError:    
    try:
        from collections import OrderedDict    
    except ImportError:
        from ordereddict import OrderedDict

class MessageError(RuntimeError):
    """
    An error has occurred while processing the message, the cause could be on
    the client side (e.g. a Timeout) or on the server side (Exception or unknown
    API call).
    """
    pass

class MessageTimeoutError(MessageError):
    """
    Raised when the message expiry time has been reached but no reply has been
    recieved.
    """
    pass

class MessageTracker(object):
    """
    Tracks messages which have been sent that are waiting for a reply.
    """
    __slots__ = ('_estor', '_kstor', '_stopevent')

    def __init__(self):
        # We must use a structure which supports ordered traversal and removal
        # of specific items, OrderedDict() is the only one I could find.
        self._estor = OrderedDict()
        self._kstor = {}
        self._stopevent = Event()

    def track(self, msg):
        """
        Start tracking a message, the returned Event is notified when a response
        is recieved or an error or timeout occurs.

        :param msg: Message Tuple 
        :returns: eventlet Event
        """        
        assert isinstance(msg, (tuple, list))
        uid = int(msg[4])
        if uid in self._kstor:
            ekey = self._kstor[uid]
            item = self._estor[ekey]
            return item[2]
        expires = int(msg[1])
        ekey = "%x%x" % (expires, uid)
        assert ekey not in self._estor
        event = Event()
        item = (uid, expires, event)
        self._estor[ekey] = item
        self._kstor[uid] = ekey
        return event

    def stop(self):
        """
        Break run() at the next interval
        """
        self._stopevent.send(True)

    def run(self, wakeup_interval=1):
        """
        Periodically check for expired messages.
        """
        stopevent = self._stopevent
        while not stopevent.ready():
            eventlet.sleep(wakeup_interval)
            self.tick(unixtime())
        ret = stopevent.wait()
        stopevent.reset()
        return ret

    def tick(self, now=None):
        """
        Remove expired messages from the Tracker
        """
        if now is None:
            now = unixtime()
        for k, item in self._estor.items():
            uid, expires, event = item
            if expires > now:
                break
            del self._estor[k]
            del self._kstor[uid]
            event.send_exception(MessageTimeoutError())

    def on_reply(self, msg):
        """
        Notify the tracker that we have recieved a message reply.
        """
        assert isinstance(msg, (tuple, list))
        try:            
            uid = msg[4]
            ekey = self._kstor[uid]
            item = self._estor[ekey]
            del self._kstor[uid]
            del self._estor[ekey]
            is_error = msg[3]
            response = msg[2]
            if is_error:
                item[2].send_exception(MessageError(response))
            else:
                item[2].send(response)            
            return True
        except KeyError:
            pass
        return False

class ServerEndpoint(object):
    __slots__ = ('_handlers', '_ctx', '_sock', '_stopevent')
    def __init__(self, bind_addr, ctx=None):
        self._handlers = {}
        self._ctx = ctx or zmq.Context.instance()
        self._sock = self._ctx.socket(zmq.XREP)
        self._sock.bind(bind_addr)
        self._stopevent = Event()

    def register(self, name, what):
        """
        Register an API call with the server, clients will use the `name` to
        call it.

        `what` must be a callable object.
        """
        assert callable(what) is True
        if name in self._handlers:
            raise RuntimeError, "Function '%s' already registered" % (name,)
        self._handlers[name] = what

    def stop(self):
        """
        Notify run() to return at the earliest convenient time
        """
        self._stopevent.send(True)

    def run(self):
        """
        Listen on the server socket and process incoming requests
        """
        sock = self._sock
        handlers = self._handlers
        stopevent = self._stopevent

        while not stopevent.ready():
            client_id, raw_msg = sock.recv_multipart()            
            if raw_msg is None:
                continue
            msg = loads(raw_msg)
            if not isinstance(msg, (list, tuple)) or len(msg) != 5:
                continue
            try:
                if not isinstance(msg[0], (list, tuple)) or len(msg[0]) != 3:
                    continue
                name, args, kwargs = msg[0]                
                if name not in handlers:
                    msg = (msg[0], msg[1], 404, True, msg[4])
                elif name[0] == '_':
                    msg = (msg[0], msg[1], 400, True, msg[4])
                else:
                    handler = handlers[name]
                    response = handler(*args, **kwargs)
                    msg = (None, msg[1], response, False, msg[4])
            except:
                msg = (msg[0], msg[1], 500, True, msg[4])
            sock.send_multipart([client_id, dumps(msg)])
        stopevent.wait()
        stopevent.reset()

class AsyncFunctionProxy(object):
    __slots__ = ('_name', '_client')
    def __init__(self, name, client):
        self._name = name
        self._client = client

    def __call__(self, *args, **kwargs):
        """
        :returns: eventlet Event to wait for result (or error)
        """
        msg = (self._name, args, kwargs)
        return self._client.send(msg)

class SyncFunctionProxy(AsyncFunctionProxy):
    def __init__(self, name, client):
        super(SyncFunctionProxy, self).__init__(name, client)

    def __call__(self, *args, **kwargs):
        return super(SyncFunctionProxy, self).__call__(*args, **kwargs).wait()

class ClientEndpoint(object):
    __slots__ = ('_ctx', '_sock', '_tracker', '_seq', '_stopevent')
    def __init__(self, server_addr, ctx=None):
        self._seq = 0
        self._ctx = ctx or zmq.Context.instance()
        self._sock = self._ctx.socket(zmq.XREQ)
        if not isinstance(server_addr, (list, tuple)):
            server_addr = [server_addr]
        for addr in server_addr:
            self._sock.connect(addr)
        self._tracker = MessageTracker()  
        self._stopevent = Event()

    def send(self, args):
        assert isinstance(args, (list, tuple))
        self._seq += 1
        msg = (args, 0xFFFFFFFF, None, None, self._seq)
        self._sock.send(dumps(msg))
        return self._tracker.track(msg)                

    def run(self):
        """
        Listen for and process replies as they come in
        """
        stopevent = self._stopevent
        sock = self._sock
        tracker = self._tracker
        eventlet.spawn_n(tracker.run)      
        while not stopevent.ready():
            raw_msg = sock.recv()
            if raw_msg is not None:                
                msg = loads(raw_msg)
                if isinstance(msg, (list, tuple)):
                    tracker.on_reply(msg)
        ret = stopevent.wait()
        stopevent.reset()
        return ret

    def stop(self):
        """
        Stop the run() method at the next convenient time.
        """
        self._stopevent.send(True)
        self._tracker.stop()

    def call(self, name, async=True):
        """        
        >>> client.call("ping")().wait() == "pong"

        >>> client.call("ping", False) == "pong"

        :param name: Name of remote method to call
        :param async: Should calls be asynchronous
        :returns: callable object
        """
        if async:
            return AsyncFunctionProxy(name, self)
        else:
            return SyncFunctionProxy(name, self)

    def asyncproxy(self, obj):
        """
        The same as proxy(), but each proxied method call will return an 
        eventlet Event which will recieve the result or exception.
        """
        return self.proxy(obj, AsyncFunctionProxy)

    def proxy(self, obj, proxyclass=SyncFunctionProxy):
        """
        Create a proxy object with the same callable methods as the given object
        that can be used as a drop-in replacement.

        All calls to proxied methods will be synchronous, blocking the callee
        until a result or exception is ready.

        :param obj: Object to proxy
        :returns: Proxy object
        """
        methods = {}
        for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
            assert callable(method)
            if name[0] == '_':
                continue
            methods[name] = proxyclass(name, self)
        return type('RpcProxy', (object,), methods)

class Impl(object):
    def __init__(self):
        self.cnt = 0

    def ping(self, msg):
        self.cnt += 1
        return 2

def main():    
    server_addr = 'inproc://server'

    impl = Impl()

    #if run_server:
    server = ServerEndpoint(server_addr)
    server.register('ping', impl.ping)
    eventlet.spawn(server.run)

    client = ClientEndpoint(server_addr)
    eventlet.spawn(client.run)

    proxyobj = client.proxy(Impl)

    iter_count = 10000
    start_time = time.time()
    i = 0
    the_call = client.call("ping")
    while 1:
        waited = False
        i += 1
        if i > iter_count:
            break
        r = the_call("World")
        if True or i % 1000 == 0:
            waited = True
            assert r.wait() == 2
    if not waited:
        r.wait()
    end_time = time.time()
    duration = end_time - start_time
    print "%f seconds per call - %d calls per second" % (duration / iter_count, iter_count/duration)

    client.stop()

if __name__ == "__main__":
    main()