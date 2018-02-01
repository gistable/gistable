import os

from zope.interface import implements
from twisted.internet import abstract, interfaces, reactor, fdesc

class NamedPipeReader(abstract.FileDescriptor):

    def __init__(self, file_name, reactor=None):
        abstract.FileDescriptor.__init__(self, reactor=reactor)
        self.file_name = file_name
        try:
            os.mkfifo(file_name)
        except OSError:
            pass

    def startListening(self):
        self.fp = open(self.file_name, 'r+')
        fdesc.setNonBlocking(self.fp)
        self.fileno = self.fp.fileno
        self.startReading()

    def doRead(self):
        buf = self.fp.read(4096)

class NamedPipeWriter(abstract.FileDescriptor):
    def __init__(self, file_name, reactor=None):
        abstract.FileDescriptor.__init__(self, reactor=reactor)
        self.file_name = file_name
        try:
            os.mkfifo(file_name)
        except OSError:
            pass
        self.fp = open(self.file_name, 'a+')
        fdesc.setNonBlocking(self.fp)
        self.fileno = self.fp.fileno

    def startListening(self):
        self.startReading()

    def writeSomeData(self, data):
        self.fp.write(data)
        self.fp.flush()

npr = NamedPipeReader('/tmp/foobar')
npw = NamedPipeWriter('/tmp/foobar')

npr.startListening()
npw.startListening()
reactor.run()
