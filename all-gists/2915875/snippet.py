import os
import fcntl

from gevent.core import wait_read, wait_write

class GeventFD(object):
    """ Wrap a file descriptor so it can be used for non-blocking reads and writes with gevent.
        >>> stdin = GeventFD(sys.stdin.fileno())
        >>> stdin.read(5)
        'hello'
        """
    def __init__(self, fd):
        self.fd = fd
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)
        self.w_pending = ""
        self.r_pending = ""

    def read(self, total_to_read):
        remaining = total_to_read
        result = ""
        while remaining > 0:
            result += self.r_pending[:remaining]
            self.r_pending = self.r_pending[remaining:]
            remaining = total_to_read - len(result)
            if remaining <= 0:
                break
            wait_read(self.fd)
            self.r_pending += os.read(self.fd, 4096)
        assert len(result) == total_to_read, \
                "len(%r) != %s" %(result, total_to_read)
        return result

    def write(self, data):
        self.w_pending += data
        while self.w_pending:
            wait_write(self.fd)
            written = os.write(self.fd, self.w_pending)
            self.w_pending = self.w_pending[written:]
