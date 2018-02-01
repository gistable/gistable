"""starttls -- an example of wrapping a non-blocking socket with TLS.

Example:

> openssl req -new -x509 -days 365 -nodes -out /tmp/cert.crt -keyout /tmp/cert.key
> python /path/to/this-file.py
starting client: 7
starting server: 8
client said: 'hello'.
server said: "YOU SAID: 'hello'".
client said: 'STARTTLS'.
server said: 'PROCEED'.
server secured!
client secured!
client said: 'QUIT'.
server said: 'GOODBYE'.
^C

"""

import sys, socket, ssl, select, errno, functools, logging
from tornado import ioloop, iostream

TRACK_WRITERS = False


### Application

def ServerApp(stream, certfile, keyfile):
    """A server that echos back each line to the client.  It accepts
    two commands that it will not echo back:

       QUIT -- close the connection
       STARTTLS -- do a TLS handshake.
    """

    def secured():
        print 'server secured!'
        wait()

    def read(line):
        line = line.strip()
        print 'client said: %r.' % line

        if line == 'QUIT':
            write('GOODBYE')
        elif line == 'STARTTLS':
            stream.write('PROCEED\n')
            stream.starttls(
                secured,
                server_side=True,
                certfile=certfile,
                keyfile=keyfile
            )
        else:
            write('YOU SAID: %r' % line)

    def write(data):
        stream.write('%s\n' % data)
        wait()

    def wait():
        stream.read_until('\n', read)

    ## Begin
    print 'starting server: %r' % stream.socket.fileno()
    wait()

def ClientApp(stream):
    """A simple client that sends a STARTTLS command to the server,
    then closes the connection when the stream is secured."""

    def secured():
        print 'client secured!'
        write('QUIT')

    def read(line):
        line = line.strip()
        print 'server said: %r.' % line
        if line == "YOU SAID: 'hello'":
            write('STARTTLS')
        elif line == 'PROCEED':
            stream.starttls(secured)
        elif line == 'GOODBYE':
            stream.close()
        else:
            wait()

    def write(data):
        stream.write('%s\n' % data)
        wait()

    def wait():
        stream.read_until('\n', read)

    ## Begin
    print 'starting client: %r' % stream.socket.fileno()
    write('hello')


### SSL / TLS

def starttls(socket, success=None, failure=None, io=None, **options):
    """Wrap an active socket in an SSL socket."""

    ## Default Options

    options.setdefault('do_handshake_on_connect', False)
    options.setdefault('ssl_version', ssl.PROTOCOL_TLSv1)

    ## Handlers

    def done():
        """Handshake finished successfully."""

        io.remove_handler(wrapped.fileno())
        success and success(wrapped)

    def error():
        """The handshake failed."""

        if failure:
            return failure(wrapped)
        ## By default, just close the socket.
        io.remove_handler(wrapped.fileno())
        wrapped.close()

    def handshake(fd, events):
        """Handler for SSL handshake negotiation.  See Python docs for
        ssl.do_handshake()."""

        if events & io.ERROR:
            error()
            return

        try:
            new_state = io.ERROR
            wrapped.do_handshake()
            return done()
        except ssl.SSLError as exc:
            if exc.args[0] == ssl.SSL_ERROR_WANT_READ:
                new_state |= io.READ
            elif exc.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                new_state |= io.WRITE
            else:
                raise

        if new_state != state[0]:
            state[0] = new_state
            io.update_handler(fd, new_state)

    ## set up handshake state; use a list as a mutable cell.
    io = io or ioloop.IOLoop.instance()
    state = [io.ERROR]

    ## Wrap the socket; swap out handlers.
    io.remove_handler(socket.fileno())
    wrapped = SSLSocket(socket, **options)
    wrapped.setblocking(0)
    io.add_handler(wrapped.fileno(), handshake, state[0])

    ## Begin the handshake.
    handshake(wrapped.fileno(), 0)
    return wrapped

class SSLSocket(ssl.SSLSocket):
    """Override the send() and recv() methods of SSLSocket to more
    closely emulate normal non-blocking socket behavior."""

    def __init__(self, *args, **kwargs):
        super(SSLSocket, self).__init__(*args, **kwargs)

        ## The base socket class overrides these methods; re-override them.
        cls = type(self)
        self.recv = cls.recv.__get__(self, cls)
        self.send = cls.send.__get__(self, cls)

    def send(self, data, flags=0):
        if not self._sslobj:
            return socket.send(self, data, flags)
        elif flags != 0:
            raise ValueError(
                '%s.send(): non-zero flags not allowed' % self.__class__
            )

        try:
            return self.write(data)
        except ssl.SSLError as exc:
            if exc.args[0] in (ssl.SSL_ERROR_WANT_WRITE, ssl.SSL_ERROR_WANT_READ):
                raise socket.error(errno.EAGAIN)
            raise

    def recv(self, buflen=1024, flags=0):
        if not self._sslobj:
            return socket.recv(self, buflen, flags)
        elif flags != 0:
            raise ValueError(
                '%s.recv(): non-zero flags not allowed' % self.__class__
            )

        try:
            return self.read(buflen)
        except ssl.SSLError as exc:
            if exc.args[0] == ssl.SSL_ERROR_WANT_READ:
                raise socket.error(errno.EAGAIN)
            raise


### TCP

class TCPServer(object):
    """A non-blocking TCP server based on tornado's HTTPServer."""

    def __init__(self, handler, io=None):
        self.handler = handler
        self.io = io or ioloop.IOLoop.instance()
        self.socket = None

    def bind(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((addr, int(port)))
        sock.listen(128)

        self.socket = sock
        return self

    def start(self):
        self.io.add_handler(self.socket.fileno(), self._accept, self.io.READ)
        return self

    def stop(self):
        if self.socket:
            self.io.remove_handler(self.socket.fileno())
            self.socket.close()
            self.socket = None
        return self

    def _accept(self, fd, events):
        while True:
            try:
                conn, addr = self.socket.accept()
            except socket.error as exc:
                if exc[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return
            try:
                self.handler(IOStream(conn, self.io))
            except:
                logging.exception('TCPServer: setup error (%s)' % (addr,))
                self.io.remove_handler(conn.fileno())
                conn.close()

class TCPClient(object):
    """A non-blocking TCP client implemented with ioloop."""

    def __init__(self, handler, io=None):
        self.handler = handler
        self.io = io or ioloop.IOLoop.instance()
        self.socket = None

    def connect(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setblocking(0)

        try:
            sock.connect((addr, int(port)))
        except socket.error as exc:
            if exc[0] != errno.EINPROGRESS:
                raise

        self.socket = sock
        return self

    def start(self):
        ## Wait until the socket is writable to initiate the client
        ## handler.
        self.io.add_handler(self.socket.fileno(), self._ready, self.io.WRITE)
        return self

    def stop(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        return self

    def _ready(self, fd, events):
        try:
            self.io.remove_handler(fd)
            self.handler(IOStream(self.socket, self.io))
        except:
            logging.exception('TCPClient: ready error')
            self.stop()


### IO

class IOStream(iostream.IOStream):
    """Extend the tornado IOStream class with a starttls() method."""

    def starttls(self, callback=None, **options):
        ## Delay starttls until the write-buffer is emptied.
        if self._write_buffer:
            self._write_callback = functools.partial(
                self.starttls, callback, **options
            )
            return

        def success(socket):
            self.socket = socket
            self.io_loop.add_handler(
                socket.fileno(),
                self._handle_events,
                self._state
            )
            callback and callback()

        def failure(socket):
            self.socket = socket
            self.close()

        ## Wrap the socket; give startttls() control until the
        ## handshake is finished.
        starttls(self.socket, success, failure, self.io_loop, **options)

        ## Temporarily set this to None so _handle_events() doesn't
        ## self.io_loop.update_handler()
        self.socket = None


### Main Program

if __name__ == '__main__':

    ## To generate keys, use a command like this:
    ##   openssl req -new -x509 -days 365 -nodes \
    ##   -out /tmp/cert.crt -keyout /tmp/cert.key
    server = functools.partial(
        ServerApp,
        certfile='/tmp/cert.crt',
        keyfile='/tmp/cert.key'
    )

    io = ioloop.IOLoop.instance()
    S = TCPServer(server, io).bind('127.0.0.1', 9000).start()
    C = TCPClient(ClientApp, io).connect('127.0.0.1', 9000).start()
    io.start()
