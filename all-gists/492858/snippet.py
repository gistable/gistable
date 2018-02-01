#!/usr/bin/env python
#
# tap -> flume
#
# requires: python thrift bindings + compiled flume thrift binding.
#

import sys
import time
import struct

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

sys.path.extend(['ep_man', 'thriftflume'])

import tap
import memcacheConstants

from flume import ThriftFlumeEventServer

class FlumeDest(object):

    def __init__(self, host, port):
        self.transport = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = ThriftFlumeEventServer.Client(self.protocol)
        self.transport.open()

        self.n = 0

    def __call__(self, identifier, cmd, extra, key, val, cas):
        if cmd == memcacheConstants.CMD_TAP_MUTATION:
            assert key is not None
            assert val is not None
            el, flags, ttl, iflags, exp = struct.unpack(memcacheConstants.TAP_MUTATION_PKT_FMT,
                                                        extra)
            pri = ThriftFlumeEventServer.Priority.INFO
            evt = ThriftFlumeEventServer.ThriftFlumeEvent(timestamp=int(time.time()),
                                                          priority=pri,
                                                          body=val,
                                                          nanos=0,
                                                          host='localhost',
                                                          fields={'key': key,
                                                                  'flags': str(flags),
                                                                  'iflags': str(iflags),
                                                                  'exp': str(exp)})
            self.client.append(evt)
            self.n += 1
            if (self.n % 1000) == 0:
                print self.n

if __name__ == '__main__':

    dest = FlumeDest('localhost', 1234)

    tap.mainLoop(sys.argv[1:], dest)
