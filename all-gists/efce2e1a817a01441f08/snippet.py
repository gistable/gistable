import functools

from tornado.gen import Task
from tornado.ioloop import IOLoop
from tornado import stack_context
from concurrent.futures import ThreadPoolExecutor


default_executor = ThreadPoolExecutor(10)


def run_on_executor(executor=default_executor):
    def run_on_executor_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task = Task(executor.submit, func, *args, **kwargs)
            return task
        return wrapper
    return run_on_executor_decorator


def run_callback(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        callback = kwargs.pop('callback', None)
        assert callback
        res = func(*args, **kwargs)
        callback = stack_context.wrap(callback)
        IOLoop.instance().add_callback(lambda: callback(res))
    return wrapper
