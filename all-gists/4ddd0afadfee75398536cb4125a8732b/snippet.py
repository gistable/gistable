from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from tornado import gen
from tornado.concurrent import run_on_executor

THREADPOOL_MAX_WORKERS = 10
THREADPOOL_TIMEOUT_SECS = 30


def onthread(function):
    @gen.coroutine
    def decorated(self, *args, **kwargs):
        future = executed(self, *args, **kwargs)
        try:
            response = yield gen.with_timeout(
                timedelta(seconds=THREADPOOL_TIMEOUT_SECS), future)
            if isinstance(response, types.GeneratorType):  # subthreads
                response = yield gen.with_timeout(
                    timedelta(seconds=settings.THREADPOOL_TIMEOUT_SECS),
                    next(response))
        except gen.TimeoutError as exc:
            future.cancel()
            raise exc
        self.write(response)

    @run_on_executor
    def executed(*args, **kwargs):
        return function(*args, **kwargs)

    return decorated
  
# Usage
class BaseHandler(object):
    executor = ThreadPoolExecutor(max_workers=THREADPOOL_MAX_WORKERS)
    ...

class MyHandler(BaseHandler):

    @onthread
    def get(self):
        ...
        return response

class MyOtherHandler(BaseHandler):

    @onthread
    def get(self):
        yield self.couroutine()

    @gen.coroutine
    def couroutine():
        data = yield {
            'one': self.threaded_one(),
            'two': self.threaded_two(),
        }
        return data

    @run_on_executor
    def threaded_one():
        ...
        return response

    @run_on_executor
    def threaded_two():
        ...
        return response