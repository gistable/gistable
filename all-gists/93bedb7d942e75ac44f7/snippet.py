import threading
import functools

import cherrypy as cp


class MainExecutor:
    """Wrap a callable to ensure that the execution takes place on the
    MainThread based on the cherrypy.engine and the 'main' channel.

    For example:

    >>> def sample(arg): return "foo {}".format(arg)
    ...
    >>> mexec = MainExecutor(sample)
    >>> mexec("bar")
    'foo bar'
    >>> mexec("test")
    'foo test'
    """

    def __init__(self, func, bus=cp.engine):
        self.func = func
        self.bus = bus

    def __call__(self, *args, **kwargs):
        results = []
        done_event = threading.Event()
        executable = functools.partial(
            self._execute, results, done_event, *args, **kwargs)
        self.bus.subscribe('main', executable)
        done_event.wait()
        self.bus.unsubscribe('main', executable)
        success, rsp = results
        if success:
            return rsp
        else:
            raise rsp

    def _execute(self, response, done_event, *args, **kwargs):
        try:
            result = self.func(*args, **kwargs)
        except Exception as e:
            response.append(False)
            response.append(e)
        else:
            response.append(True)
            response.append(result)
        finally:
            done_event.set()


def in_main_thread(func):
    """Pretty interface to use the MainExecutor class
    as a decorator and not have the CamelCase on a decorator.
    """
    return MainExecutor(func)


class Root:

    @in_main_thread
    def compute(self, *args):
        return "Args: {}, ThreadID: {}".format(args, threading.current_thread().name)

    @cp.expose
    def default(self, *args):
        return self.compute(*args)


cp.quickstart(Root())
