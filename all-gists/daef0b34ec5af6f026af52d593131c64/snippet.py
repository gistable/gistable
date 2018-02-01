from tornado.concurrent import is_future
from tornado.gen import Return, coroutine, convert_yielded, multi_future, sleep
from tornado.ioloop import IOLoop
from tornado.locks import Event

from promise import Promise

from graphql.execution import execute
from graphql.language.parser import parse
from graphql.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLString
)


class TornadoExecutor(object):
    def __init__(self, io_loop=None):
        if io_loop is None:
            io_loop = IOLoop.current()
        self.loop = io_loop
        self.futures = []

    def wait_until_finished(self):
        # if there are futures to wait for
        while self.futures:
            # wait for the futures to finish
            futures = self.futures
            self.futures = []
            self.loop.run_sync(lambda: multi_future(futures))

    def execute(self, fn, *args, **kwargs):
        result = fn(*args, **kwargs)
        if is_future(result):
            future = convert_yielded(result)
            self.futures.append(future)
            return Promise.resolve(future)
        return result


ast = parse('query Example { a, b, c }')


def schema():
    @coroutine
    def resolver(*_):
        yield sleep(0.001)
        raise Return('hey')

    @coroutine
    def resolver_2(*_):
        yield sleep(0.003)
        raise Return('hey2')

    def resolver_3(*_):
        return 'hey3'

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2),
        'c': GraphQLField(GraphQLString, resolver=resolver_3)
    })
    return GraphQLSchema(Type)


def do_exec():
    result = execute(schema(),
                     ast,
                     executor=TornadoExecutor(IOLoop()))
    assert not result.errors
    assert result.data == {'a': 'hey', 'b': 'hey2', 'c': 'hey3'}
    print('SUCCESS SYNC')

do_exec()


@coroutine
def do_exec():
    result = execute(schema(),
                     ast,
                     executor=TornadoExecutor(),
                     return_promise=True)

    if getattr(result, 'is_pending', False):
        event = Event()
        on_resolve = lambda *_: event.set()
        result.then(on_resolve).catch(on_resolve)
        yield event.wait()

    if hasattr(result, 'get'):
        result = result.get()
    assert not result.errors
    assert result.data == {'a': 'hey', 'b': 'hey2', 'c': 'hey3'}
    print('SUCCESS ASYNC')

IOLoop().run_sync(do_exec)
