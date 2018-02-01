"""The :mod:`zmq` module wraps the :class:`Socket` and :class:`Context` found in :mod:`pyzmq <zmq>` to be non blocking
"""
__zmq__ = __import__('zmq')
from gevent.hub import _threadlocal
from gevent.socket import wait_read, wait_write

__patched__ = ['Context', 'Socket']
globals().update(dict([(var, getattr(__zmq__, var))
                       for var in __zmq__.__all__
                       if not (var.startswith('__')
                            or
                              var in __patched__)
                       ]))

def Context(io_threads=1):
    """Factory function replacement for :class:`zmq.core.context.Context`

    Ensures only be one :class:`_Context` instance per thread.
    """
    try:
        return _threadlocal.zmq_context
    except AttributeError:
        _threadlocal.zmq_context = _Context(io_threads)
        return _threadlocal.zmq_context

class _Context(__zmq__.Context):
    """Internal subclass of :class:`zmq.core.context.Context`

    .. warning:: Do not grab one of these yourself
    """

    def socket(self, socket_type):
        """Overridden method to ensure that the green version of socket is used

        Behaves the same as :meth:`zmq.core.context.Context.socket`, but ensures
        that a :class:`Socket` with all of its send and recv methods set to be
        non-blocking is returned
        """
        return Socket(self, socket_type)

class Socket(__zmq__.Socket):
    """Green version of :class:`zmq.core.socket.Socket

    The following four methods are overridden:

        * _send_message
        * _send_copy
        * _recv_message
        * _recv_copy

    To ensure that the ``zmq.NOBLOCK`` flag is set and that sending or recieving
    is deferred to the hub if a ``zmq.EAGAIN`` (retry) error is raised
    """


    def _send_message(self, msg, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                super(Socket, self)._send_message(msg, flags)
                return
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            wait_write(self.getsockopt(__zmq__.FD))

    def _send_copy(self, msg, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                super(Socket, self)._send_copy(msg, flags)
                return
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            wait_write(self.getsockopt(__zmq__.FD))

    def _recv_message(self, flags=0, track=False):

        flags |= __zmq__.NOBLOCK
        while True:
            try:
                m = super(Socket, self)._recv_message(flags, track)
                if m is not None:
                    return m
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            wait_read(self.getsockopt(__zmq__.FD))

    def _recv_copy(self, flags=0):
        flags |= __zmq__.NOBLOCK
        while True:
            try:
                m = super(Socket, self)._recv_copy(flags)
                if m is not None:
                    return m
            except __zmq__.ZMQError, e:
                if e.errno != EAGAIN:
                    raise
            wait_read(self.getsockopt(__zmq__.FD))



