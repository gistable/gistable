from cassandra.cluster import Cluster, OperationTimedOut
from cassandra.decoder import SyntaxException

from tornado.concurrent import Future
from tornado.testing import AsyncTestCase, gen_test


class TornadoCassandra(object):

    def __init__(self, session, ioloop):
        self._session = session
        self._ioloop = ioloop

    def execute(self, *args, **kwargs):
        tornado_future = Future()
        cassandra_future = self._session.execute_async(*args, **kwargs)
        self._ioloop.add_callback(
            self._callback, cassandra_future, tornado_future)
        return tornado_future

    def _callback(self, cassandra_future, tornado_future):
        try:
            # should spend just about no time blocking.
            result = cassandra_future.result(timeout=0)
        except OperationTimedOut:
            return self._ioloop.add_callback(
                self._callback, cassandra_future, tornado_future)
        except Exception, exc:
            return tornado_future.set_exception(exc)
        tornado_future.set_result(result)


class TestTornadoCassandra(AsyncTestCase):

    def setUp(self):
        super(TestTornadoCassandra, self).setUp()
        self.cluster = Cluster(["127.0.0.1"])
        self.session = self.cluster.connect()
        self.session.execute(
            "CREATE KEYSPACE IF NOT EXISTS testingfuture WITH REPLICATION = "
            "{ 'class': 'SimpleStrategy', 'replication_factor': 1 }")
        self.session.execute("USE testingfuture;")
        self.session.execute(
            "CREATE TABLE IF NOT EXISTS footable (\n"
            "key VARCHAR, \n"
            "url VARCHAR, \n"
            "PRIMARY KEY (key));")
        self.session.execute(
            "INSERT INTO footable (key, url) "
            "VALUES (%s, %s)", ("foobar", "http://foo.com"))
        self.connection = TornadoCassandra(self.session, ioloop=self.io_loop)

    def tearDown(self):
        super(TestTornadoCassandra, self).tearDown()
        self.session.execute("DROP KEYSPACE testingfuture;")

    @gen_test
    def test_query(self):
        results = yield self.connection.execute(
            "SELECT key, url FROM footable;")
        self.assertEqual(1, len(results))
        self.assertEqual(("foobar", "http://foo.com"), results[0])

    @gen_test
    def test_exception(self):
        with self.assertRaises(SyntaxException):
            yield self.connection.execute("foobar!")

    @gen_test
    def test_lots_of_queries(self):
        futures = []
        count = 2048
        for i in range(count):
            futures.append(self.connection.execute(
                "SELECT key FROM footable;"))
        results = 0
        for future in futures:
            yield future
            results += 1
        self.assertEqual(count, results)