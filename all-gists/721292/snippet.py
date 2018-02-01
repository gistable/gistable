from twisted.internet import main, reactor
from twisted.internet.abstract import FileDescriptor
from twisted.internet.error import ConnectionDone
from twisted.internet.fdesc import setNonBlocking
from twisted.internet.interfaces import IReadDescriptor
from twisted.internet.protocol import Protocol
from twisted.python import log
from twisted.python.failure import Failure
from twisted.python.filepath import FilePath
from zope.interface import implements
import errno
import os
import sys


class FIFO(FileDescriptor):
    chunk_size = 2
    implements(IReadDescriptor)
    
    def __init__(self, path, _reactor=None):
        self._fd = None
        self._path = path
        FileDescriptor.__init__(self, _reactor)
    
    def startReading(self):
        if self._fd is not None and not self._fd.closed:
            FileDescriptor.startReading(self)
            return
        self._fd = self._path.open('r')
        setNonBlocking(self._fd)
        FileDescriptor.startReading(self)
    
    def fileno(self):
        return self._fd.fileno()
    
    def doRead(self):
        while True:
            try:
                output = os.read(self.fileno(), self.chunk_size)
            except (OSError, IOError), err:
                if err.args[0] in (errno.EAGAIN, errno.EINTR):
                    return
                else:
                    return main.CONNECTION_LOST
            if not output:
                return main.CONNECTION_DONE
            self.protocol.dataReceived(output)
    
    def connectionLost(self, reason):
        FileDescriptor.connectionLost(self, reason)
        self.protocol.connectionLost(reason)
            
    def logPrefix(self):
        return "%s: %s" % (self.__class__.__name__, self._path.path) 
            

class FIFOListener(Protocol):
    
    def __init__(self, path, _reactor=None):
        if _reactor is not None:
            self._reactor = _reactor
        else:
            self._reactor = reactor
        self.path = path
    
    def startListening(self):
        self.fdesc = FIFO(self.path, self._reactor)
        self.fdesc.protocol = self
        self.makeConnection(self.fdesc)
    
    def dataReceived(self, data):
        log.msg("Got data from fifo: %s" % data)
    
    def connectionLost(self, reason):
        if reason.check(ConnectionDone) is not None:
            self.startListening()
        else:
            log.err(reason)
    
    def connectionMade(self):
        try:
            self.transport.startReading()
        except (OSError, IOError), err:
            self.connectionLost(Failure(err))


def _main():
    log.startLogging(sys.stdout)
    proto = FIFOListener(FilePath('foo'))
    proto.startListening()

if __name__ == '__main__':
    reactor.callWhenRunning(_main)
    reactor.run()
    
