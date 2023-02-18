"""
Graceful Stopper
===================
Tool to stop a TCPServer (or HTTPServer) in a graceful manner (when the all
currently running work is done). This script works either for forked servers or
single-process servers.

The graceful-stop process can be triggered by sending `SIGHUP` to server (in a
forked environment, sending SIGHUP to main server, propagates to all
children). Server immediately releases the listening socket (so another server
can be launched on that port) and wait for running requests to finish. The
server is also stops if stop-timeout is reached (defaults to 100 seconds, can
be changed or disabled).

Usage
-------------------
1. single-process `GracefulHTTPServer` using `listen`:

    server = GracefulHTTPServer()
    server.listen(8888)
    IOLoop.instance().start()

2. multi-process `GracefulHTTPServer` using `start`:

    server = GracefulHTTPServer()
    server.bind(8888)
    server.start(0)  # Forks multiple sub-processes
    IOLoop.instance().start()

3. advanced multi-process `GracefulHTTPServer` using `add_sockets`

    sockets = tornado.netutil.bind_sockets(8888)
    server = GracefulHTTPServer()  # should be before fork
    tornado.process.fork_processes(0)
    server.add_sockets(sockets)
    IOLoop.instance().start()

4. advanced usage of `GracefulServerStopper` for any TCPServer

    stopper = GracefulServerStopper()  # should be called before fork, (server
                                       # can be passed inline as keyword arg)
    server = HTTPServer()
    server.bind(8888)
    server.start(0)
    stopper.server = server  # can be called before or after fork
    stopper.setup_worker_handlers()  # should be called after fork
    IOLoop.instance().start()

Customizing stop behaviour
-------------------
Detecting the WORK_DONE state is not so easy, the simplest way is to watch
IOLoop queue to be empty, but there may be resident handlers in IOLoop queue,
so io-loop is always not-empty. (periodic callbacks (e.g. monitoring tasks),
persistent database connections, ...)

Behaviour of detecting WORK_DONE state is encapsulated and can be changed via
setting `work_done_detector` attribute on stopper (can be passed by
`work_done_detector` keyword argument to `GracefulHTTPServer`
or `GracefulServerStopper`)

Also there is more advanced `RequestInspectorWorkDoneDetector` that inspects
callbacks in IOLoop and detects the WORK_DONE state when there is not
`HTTPRequest` is in progress.
(Uses [tornado-inspector](https://github.com/tahajahangir/tornado-inspector))
"""
import logging
import os
import signal
from tornado.httpserver import HTTPServer
from tornado.ioloop import PeriodicCallback
from tornado.tcpserver import TCPServer


logger = logging.getLogger('tornado.general.graceful')


class BaseWorkDoneDetectionStrategy(object):
    def is_work_done(self, io_loop):
        raise NotImplementedError


class MinHandlerWorkDoneDetector(BaseWorkDoneDetectionStrategy):
    def is_work_done(self, io_loop):
        # noinspection PyProtectedMember
        return len(io_loop._handlers) <= 1


class RequestInspectorWorkDoneDetector(BaseWorkDoneDetectionStrategy):
    # noinspection PyProtectedMember
    def is_work_done(self, io_loop):
        # see https://github.com/tahajahangir/tornado-inspector
        from tornado_inspector import TornadoContextInspector
        inspector = TornadoContextInspector(stop_on_request_find=True)
        for callback in io_loop._handlers.itervalues():
            inspector.inspect_callback(callback)
            if inspector.found_req:
                return False
        return True


class GracefulServerStopper(object):
    stop_signal = signal.SIGHUP
    try_stop_period = 1000  # milliseconds, After call to 'graceful_stop', try to stop, every N milliseconds

    def __init__(self, server=None, work_done_detector=None, max_wait_seconds=100):
        """
        The `server` and `work_done_detector` is required at run-time, but can be set after initialization or after fork
        NOTE: GracefulServerStopper instance SHOULD be created before fork

        @param server: The `TCPServer` instance (or subclasses like HTTPServer)
        @param work_done_detector: the strategy to detect if work is done or not
        @param max_wait_seconds: the timeout for server to stop, set to None to disable
        @type server: tornado.tcpserver.TCPServer
        @type work_done_detector: BaseWorkDoneDetectionStrategy
        """
        self.server = server
        self.work_done_detector = work_done_detector
        self.max_wait_seconds = max_wait_seconds
        self._stopped = False
        self.setup_main_handlers()

    def setup_main_handlers(self):
        """
        Setup signal handler for the main process (process that calls `process.fork_processes`)
        Installed handler will be overwritten by `setup_worker_handlers` on child processes
        NOTE: This should be called before `process.fork_processes` call
        """
        def propagate_signal_to_children(signum, frame):
            # find the children dict in `process.fork_processes`
            while frame:
                if frame.f_code.co_name == 'fork_processes' and isinstance(frame.f_locals.get('children'), dict):
                    children = frame.f_locals['children']
                    break
                frame = frame.f_back
            else:
                logger.error('Cannot find `children` dict, ignoring signal')
                return
            # propagate signal
            sig_name = [k for k, v in signal.__dict__.iteritems() if k.startswith('SIG') and v == signum]
            logger.info('Propagating signal %s(%d) to children %s' % (sig_name[0] if signum else 'UNKNOWN', signum,
                        ', '.join(str(pid) for pid in children)))
            for pid in children:
                os.kill(pid, signum)
            exit(0)  # exit immediately, prevent spawning new child, if in middle of re-creating a child

        signal.signal(self.stop_signal, propagate_signal_to_children)

    def _stop_if_work_done(self):
        if self.work_done_detector is None:
            self.work_done_detector = MinHandlerWorkDoneDetector()
        work_done = True if not self.work_done_detector else self.work_done_detector.is_work_done(self.server.io_loop)
        if work_done:
            logger.info("Graceful shutdown complete. Exiting!")
            self.hard_stop()
        else:
            # noinspection PyProtectedMember
            logger.info("Waiting for io_loop to be empty. has %d handlers left" % len(self.server.io_loop._handlers))

    def hard_stop(self):
        self.server.io_loop.stop()

    def graceful_stop(self):
        if self._stopped:
            logger.info("Graceful shutdown has already begun")
            return

        def timed_out_handler(*_):
            logger.info("worker timeout reached with SIGALRM, stopping")
            self.hard_stop()

        logger.info("Waiting for all connections to finish or %s seconds to pass (setting SIGALRM)" %
                    str(self.max_wait_seconds))

        self._stopped = True
        self.server.stop()  # stop to accepting new connections, release listening socket
        if self.max_wait_seconds is not None:
            signal.signal(signal.SIGALRM, timed_out_handler)
            signal.alarm(self.max_wait_seconds)
        PeriodicCallback(self._stop_if_work_done, self.try_stop_period, io_loop=self.server.io_loop).start()

    def setup_worker_handlers(self):
        def graceful_shutdown_handler(signum, _):
            logger.info("Received signal %d. Starting graceful shutdown process" % signum)
            self.graceful_stop()

        signal.signal(self.stop_signal, graceful_shutdown_handler)
        signal.siginterrupt(self.stop_signal, False)  # prevent interrupted system call errors


class GracefulHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        self.stopper = kwargs.pop('stopper', None) or GracefulServerStopper(self)
        super(GracefulHTTPServer, self).__init__(*args, **kwargs)

    def add_sockets(self, sockets):
        super(GracefulHTTPServer, self).add_sockets(sockets)
        self.stopper.setup_worker_handlers()


class GracefulTCPServer(TCPServer):
    def __init__(self, *args, **kwargs):
        self.stopper = kwargs.pop('stopper', None) or GracefulServerStopper(self)
        self.stopper.work_done_detector = kwargs.pop('work_done_detector', None)
        super(GracefulTCPServer, self).__init__(*args, **kwargs)

    def add_sockets(self, sockets):
        super(GracefulTCPServer, self).add_sockets(sockets)
        self.stopper.setup_worker_handlers()
