from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from asyncio import iscoroutine
from tornado import gen
from graphql.core.pyutils.defer import Deferred


def process_future_result(deferred):
    def handle_future_result(future):
        exception = future.exception()
        if exception:
            deferred.errback(exception)
        else:
            deferred.callback(future.result())

    return handle_future_result


class TornadoExecutionMiddleware(object):
    @staticmethod
    def run_resolve_fn(resolver, original_resolver):
        result = resolver()
        if isinstance(result, Future) or iscoroutine(result):
            future = gen.convert_yielded(result)
            d = Deferred()
            IOLoop.current().add_future(future, process_future_result(d))
            return d

        # Si no es future ni corutina
        return result

    @staticmethod
    def execution_result(executor):
        future = Future()
        result = executor()
        assert isinstance(result, Deferred), 'Another middleware has converted the execution result ' \
                                             'away from a Deferred.'

        result.add_callbacks(future.set_result, future.set_exception)
        return future
