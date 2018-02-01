import os, time, functools, types, unittest
from tornado import gen, ioloop

import asyncmongo
import asyncmongo.errors

def async_test_engine(timeout_sec=5):
    if not isinstance(timeout_sec, int) and not isinstance(timeout_sec, float):
        raise TypeError(
            "Expected int or float, got %s\n"
            "Use async_test_engine like:\n\t@async_test_engine()\n"
            "or:\n\t@async_test_engine(5)" % (
                repr(timeout_sec)
                )
        )

    timeout_sec = max(timeout_sec, float(os.environ.get('TIMEOUT_SEC', 0)))

    def decorator(func):
        class AsyncTestRunner(gen.Runner):
            def __init__(self, gen, timeout):
                super(AsyncTestRunner, self).__init__(gen)
                self.timeout = timeout

            def run(self):
                loop = ioloop.IOLoop.instance()
                try:
                    super(AsyncTestRunner, self).run()
                except Exception:
                    loop.remove_timeout(self.timeout)
                    loop.stop()
                    raise

                if self.finished:
                    loop.remove_timeout(self.timeout)
                    loop.stop()

        @functools.wraps(func)
        def _async_test(self):
            loop = ioloop.IOLoop.instance()

            def on_timeout():
                loop.stop()
                raise AssertionError("%s timed out" % func)

            timeout = loop.add_timeout(time.time() + timeout_sec, on_timeout)

            gen = func(self)
            assert isinstance(gen, types.GeneratorType), (
                "%s should be a generator, include a yield "
                "statement" % func
                )

            AsyncTestRunner(gen, timeout).run()

            loop.start()
        return _async_test
    return decorator

async_test_engine.__test__ = False # Nose otherwise mistakes it for a test


class AssertRaises(gen.Task):
    def __init__(self, exc_type, func, *args, **kwargs):
        super(AssertRaises, self).__init__(func, *args, **kwargs)
        if not isinstance(exc_type, type):
            raise TypeError("%s is not a class" % repr(exc_type))

        if not issubclass(exc_type, Exception):
            raise TypeError(
                "%s is not a subclass of Exception" % repr(exc_type))
        self.exc_type = exc_type

    def get_result(self):
        args, kwargs = self.runner.pop_result(self.key)
        error = kwargs.get('error')
        if not isinstance(error, self.exc_type):
            if error:
                raise AssertionError("%s raised instead of %s" % (
                    repr(error), self.exc_type.__name__))
            else:
                raise AssertionError("%s not raised" % self.exc_type.__name__)
        return args[0]


class AssertEqual(gen.Task):
    def __init__(self, expected, func, *args, **kwargs):
        super(AssertEqual, self).__init__(func, *args, **kwargs)
        self.expected = expected

    def get_result(self):
        args, kwargs = self.runner.pop_result(self.key)
        if kwargs.get('error'):
            raise kwargs['error']

        result = args[0]
        if self.expected != result:
            raise AssertionError("%s returned %s, not %s" % (
                self.func, repr(result), repr(self.expected)))

        return result


class MyTestCase(unittest.TestCase):
    @async_test_engine(timeout_sec=2)
    def test_stuff(self):
        db = asyncmongo.Client(
            pool_id='test_query',
            host='127.0.0.1',
            port=27017,
            dbname='test',
            mincached=3
        )

        yield gen.Task(db.collection.remove, safe=True)
        yield gen.Task(db.collection.insert, {"_id" : 1}, safe=True)

        # Verify the document was inserted
        yield AssertEqual([{'_id': 1}], db.collection.find)

        # MongoDB has a unique index on _id
        yield AssertRaises(
              asyncmongo.errors.IntegrityError,
              db.collection.insert, {"_id" : 1}, safe=True)

if __name__ == '__main__':
    unittest.main()