import logging
log = logging.getLogger('socrates')

from Queue import Empty, Full, Queue

from riak.transports import RiakPbcTransport
from riak.transports.transport import RiakTransport


class PbcPoolTransport(RiakTransport):
    """Threadsafe pool of PBC connections, based on urllib3's pool [aka Queue]"""
    def __init__(self, host='127.0.0.1', port=8087, client_id=None, maxsize=0, block=False, timeout=None):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.block = block
        self.timeout = timeout

        self.pool = Queue(None)
        [self.pool.put(None) for _ in xrange(maxsize)]

        self.num_connections = 0
        self.num_requests = 0

    def _new_conn(self):
        """New PBC connection"""
        self.num_connections += 1
        log.info('Starting new connection (%d): %s', self.num_connections, self.host)
        return RiakPbcTransport(self.host, self.port, self.client_id)

    def _get_conn(self):
        conn = None
        try:
            conn = self.pool.get(block=self.block, timeout=self.timeout)
        except Empty, e:
            pass
        return conn or self._new_conn()

    def _put_conn(self, conn):
        try:
            self.pool.put(conn, block=False)
        except Full, e:
            self.num_connections -= 1
            # conn.close()
            log.warning("Connection pool is full, discarding connection: %s", self.host)

    def _make_call(self, function):
        """checkout conn, try operation, put conn back in pool"""
        self.num_requests += 1
        conn = None
        rv = None
        try:
            conn = self._get_conn()
            rv = function(conn)
        finally:
            self._put_conn(conn)
        return rv

    def ping(self):
        """
        Ping the remote server
        @return boolean
        """
        return self._make_call(lambda conn: conn.ping())

    def get(self, robj, r = None, vtag = None):
        """
        Serialize get request and deserialize response
        @return (vclock=None, [(metadata, value)]=None)
        """
        return self._make_call(lambda conn: conn.get(robj, r, vtag))

    def put(self, robj, w = None, dw = None, return_body = True):
        """
        Serialize put request and deserialize response - if 'content'
        is true, retrieve the updated metadata/content
        @return (vclock=None, [(metadata, value)]=None)
        """
        return self._make_call(lambda conn: conn.put(robj, w, dw, return_body))

    def delete(self, robj, rw = None):
        """
        Serialize delete request and deserialize response
        @return true
        """
        return self._make_call(lambda conn: conn.delete(robj, rw))

    def get_bucket_props(self, bucket) :
        """
        Serialize get bucket property request and deserialize response
        @return dict()
        """
        return self._make_call(lambda conn: conn.get_bucket_props(bucket))

    def set_bucket_props(self, bucket, props) :
        """
        Serialize set bucket property request and deserialize response
        bucket = bucket object
        props = dictionary of properties
        @return boolean
        """
        return self._make_call(lambda conn: conn.set_bucket_props(bucket, props))

    def mapred(self, inputs, query, timeout = None) :
        """
        Serialize map/reduce request
        """
        return self._make_call(lambda conn: conn.mapred(inputs, query, timeout))

    def set_client_id(self, client_id):
        """Uh hrm, this statefulness needs to persist better to manually call _get_conn etc"""
        return self._make_call(lambda conn: conn.set_client_id(client_id))
