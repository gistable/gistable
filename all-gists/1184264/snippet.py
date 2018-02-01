# Copyright 2011 10gen
# 
# Modified by Antonin Amand <antonin.amand@gmail.com> to work with gevent.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import pymongo.connection
from gevent.hub import getcurrent
import gevent.queue
import gevent.greenlet
import gevent.local
import gevent.coros
from gevent import socket
import weakref


class Pool(object):
    """ A greenlet safe connection pool for gevent (non-thread safe).
    """

    DEFAULT_TIMEOUT = 3.0

    def __init__(self, pool_size, network_timeout=None):
        self.network_timeout = network_timeout or self.DEFAULT_TIMEOUT
        self.pool_size = pool_size
        self._bootstrap(os.getpid())
        self._lock = gevent.coros.RLock()

    def _bootstrap(self, pid):
        self._count = 0
        self._pid = pid
        self._used = {}
        self._queue = gevent.queue.Queue(self.pool_size)

    def connect(self, host, port):
        """Connect to Mongo and return a new (connected) socket.
        """
        try:
            # Prefer IPv4. If there is demand for an option
            # to specify one or the other we can add it later.
            s = socket.socket(socket.AF_INET)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(self.network_timeout or 
                    pymongo.connection._CONNECT_TIMEOUT)
            s.connect((host, port))
            s.settimeout(self.network_timeout)
            return s
        except socket.gaierror:
            # If that fails try IPv6
            s = socket.socket(socket.AF_INET6)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(self.network_timeout or 
                    pymongo.connection._CONNECT_TIMEOUT)
            s.connect((host, port))
            s.settimeout(self.network_timeout)
            return s

    def get_socket(self, host, port):
        pid = os.getpid()
        if pid != self._pid:
            self._bootstrap(pid)

        greenlet = getcurrent()
        from_pool = True
        sock = self._used.get(greenlet)
        if sock is None:
            with self._lock:
                if self._count < self.pool_size:
                    self._count += 1
                    from_pool = False
                    sock = self.connect(host, port)
        if sock is None:
            from_pool = True
            sock = self._queue.get(timeout=self.network_timeout)

        if isinstance(greenlet, gevent.Greenlet):
            greenlet.link(self._return)
            self._used[greenlet] = sock
        else:
            ref = weakref.ref(greenlet, self._return)
            self._used[ref] = sock
        return sock, from_pool

    def return_socket(self):
        greenlet = getcurrent()
        self._return(greenlet)

    def _return(self, greenlet):
        try:
            sock = self._used.get(greenlet)
            if sock is not None:
                del self._used[greenlet]
                self._queue.put(sock)
        except:
            with self._lock:
                self._count -= 1


def patch():
    import pymongo.connection
    pymongo.connection._Pool = Pool

