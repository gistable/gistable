import errno
import socket
from threading import Thread
from tornado import ioloop


class IOLoopThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.io_loop = ioloop.IOLoop.instance()

    def run(self):
        self.io_loop.start()

    def shutdown(self):
        self.io_loop.stop()


class Client(object):
    """
    The TCP Client class
        c = Client("test.myhost.com", 4242)
        c.start()
    """
    def __init__(self, host, port, id):
        self.id = id
        self.read_chunk_size = 1024
        self.host = host
        self.port = port
        self.io_loop = ioloop.IOLoop.instance()
        self.finished = False

    def start(self):
        # 1. establish a TCP connection to the flock server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(0)

        # 2. add to tornado for receiving a callback when we receive data
        self.io_loop.add_handler(
            self.sock.fileno(), self._handle_events, self.io_loop.ERROR)
        self.io_loop.update_handler(self.sock.fileno(), self.io_loop.READ)

        # 3. visual output to console
        # sys.stdout.write(".")
        # sys.stdout.flush()

    def _handle_events(self, fd, events):
        if not self.sock:
            print "Got events for closed stream %d" % fd
            return
        if events & self.io_loop.READ:
            self._handle_read()
        if events & self.io_loop.ERROR:
            self._close_socket()
            return

    def _close_socket(self):
        try:
            self.io_loop.remove_handler(self.sock.fileno())
        except:
            pass

        if self.sock:
            self.sock.close()
            self.sock = None

    def _handle_read(self):
        """Signal by epoll: data chunk ready to read from socket buffer."""
        try:
            chunk = self.sock.recv(self.read_chunk_size)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return
            else:
                print "Read error on %d: %s" % (self.fileno, e)
                self._close_socket()
                return

        # empty data means closed socket per TCP specs
        if not chunk:
            self._close_socket()
            return

        # Print response
        print "[%s:%s] chunk: %s" % (self.host, self.port, repr(chunk))


def main():
    running = True
    t = IOLoopThread()
    t.start()

    targets = [
        ["127.0.0.1", 4000],
        ["127.0.0.1", 4001],
    ]
    try:
        clients = []
        print "Connecting clients..."
        for i in xrange(len(targets)):
            host, port = targets[i]
            print "- %s:%s" % (host, port)
            c = Client(host, port, i)
            c.start()
            clients.append(c)

        print "Enter your commands or 'quit':"
        while running:
            i = raw_input("")
            if i:
                if i == "quit":
                    running = False
                else:
                    for c in clients:
                        c.sock.send("%s\n" % i.strip())

    except Exception as e:
        raise e

    finally:
        t.shutdown()


if __name__ == "__main__":
	main()