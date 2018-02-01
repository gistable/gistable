class ThriftConnection(object):
    def __init__(self, service, host, port):
        socket = TSocket.TSocket(host, port)
        self.transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocolAccelerated(self.transport)
        self.client = service.Client(protocol)
        self.transport.open()
        self.open_time = time.time()
        self.access_time = self.open_time
        self.str = "%s#%d(%s:%d/%s)" % (self.__class__.__name__, id(self), host, port, service.__name__.rsplit(".", 1)[-1])

    def close(self):
        try:
            self.transport.close()
        except Exception:
            pass

    def touch(self):
        self.access_time = time.time()

    def __str__(self):
        return self.str


class ThriftServer(object):
    def __init__(self, service, host, port):
        self.service = service
        self.host = host
        self.port = port

    def acquire(self):
        return ThriftConnection(self.service, self.host, self.port)

    def release(self, conn):
        conn.close()

    def abandon(self, conn):
        conn.close()

    @contextmanager
    def client(self):
        conn = self.acquire()
        try:
            yield conn.client
        finally:
            self.release(conn)

    def __str__(self):
        return "%s#%d(%s:%d/%s)" % (self.__class__.__name__, id(self), self.host, self.port, self.service.__name__.rsplit(".", 1)[-1])


class ThriftPool(object):
    def __init__(self, service, host, port, pool_conf=None):
        self.pid = os.getpid()
        self.service = service
        self.host = host
        self.port = port
        self.pool_conf = {"max": 0, "min": 1, "timeout": 0.1, "idle_timeout": 30, "max_lifetime": 30 * 60}
        if pool_conf:
            self.pool_conf.update(pool_conf)
        self.pool_timeout = self.pool_conf["timeout"]
        self.pool_idle_timeout = self.pool_conf["idle_timeout"]
        self.pool_max_lifetime = self.pool_conf["max_lifetime"]
        self.pool = LifoQueue(self.pool_conf["max"])
        self.diet()

    def dispose(self):
        self.clear()

    def clear(self):
        while True:
            try:
                conn = self.pool.get(block=False)
                if conn:
                    self.abandon(conn)
            except Empty:
                break

    def diet(self):
        for i in range(self.pool_conf["min"]):
            try:
                self.pool.put(None, block=False)
            except Full:
                break

    def acquire(self):
        conn = None
        try:
            conn = self.pool.get(block=True, timeout=self.pool_timeout)
        except Empty:
            logger.warning("No idle connection, create one more.")
        if conn:
            now = time.time()
            if (now - conn.access_time > self.pool_idle_timeout) or (now - conn.open_time > self.pool_max_lifetime):
                logger.info("Discard obsolete connection %s." % conn)
                conn.close()
                conn = None
        return conn or ThriftConnection(self.service, self.host, self.port)

    def release(self, conn):
        try:
            conn.touch()
            self.pool.put(conn, block=False)
        except Full:
            logger.warning("The pool is full, discard connection %s." % conn)
            conn.close()

    def abandon(self, conn):
        conn.close()
        self.clear()
        self.diet()

    @contextmanager
    def client(self):
        if os.getpid() != self.pid:
            logger.info("This pool is created by other process, reinitializing it.")
            self.dispose()
            self.__init__(self.service, self.host, self.port, pool_conf=self.pool_conf)
        conn = self.acquire()
        try:
            yield conn.client
            self.release(conn)
        except Thrift.TException:
            self.abandon(conn)
            raise
        except:
            self.release(conn)
            raise

    def __str__(self):
        return "%s#%d(%s:%d/%s)" % (self.__class__.__name__, id(self), self.host, self.port, self.service.__name__.rsplit(".", 1)[-1])


class ThriftHA(object):
    def __init__(self, replicas):
        self.replicas = replicas[:]
        self.retry = len(self.replicas) + 1
        self.unavailable = {}

    def pick_available(self):
        # logger.debug("Pick one from available ones.")
        for replica in self.replicas:
            if replica not in self.unavailable:
                return replica
            if time.time() > self.unavailable[replica][1]:
                logger.info("Give a chance to %s." % replica)
                return replica
        logger.info("All replicas are unavailable. Give a chance to the primary.")
        return self.replicas[0]

    def mark_unavailable(self, replica):
        count = self.unavailable.get(replica, (0, None))[0] + 1
        duration = 2 ** min(count, 10)
        logger.info("Mark %s as unavailable. Backoff %d seconds." % (replica, duration))
        self.unavailable[replica] = (count, time.time() + duration)

    def mark_available(self, replica):
        if replica in self.unavailable:
            logger.info("Mark %s as available." % replica)
            del self.unavailable[replica]

    @contextmanager
    def client(self):
        acquire_error = None
        for i in xrange(self.retry):
            # logger.debug("Trying to acquire a connection.")
            try:
                replica = self.pick_available()
                conn = replica.acquire()
                acquire_error = None
                self.mark_available(replica)
                # logger.debug("Acquired %s from %s." % (conn, replica))
                break
            except Exception, e:
                logger.exception("Error while acquiring a connection from %s." % replica)
                acquire_error = e
                self.mark_unavailable(replica)
        if acquire_error is not None:
            logger.error("No available replica.")
            raise acquire_error
        try:
            yield conn.client
            replica.release(conn)
        except Thrift.TException:
            replica.abandon(conn)
            self.mark_unavailable(replica)
            raise
        except:
            replica.release(conn)
            raise


helloworld = ThriftHA([ThriftPool(HelloWorld, host, 1234, pool_conf={"max": 3}) for host in ["primary.localdomain", "fallback.localdomain"]])
with helloworld.client() as client:
    print client.hello("world")
