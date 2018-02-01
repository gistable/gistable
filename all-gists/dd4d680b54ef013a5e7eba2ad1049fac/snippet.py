
#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~
#
# >>
#   .. created: 5/20/16
#   .. author:  blake.vandemerwe
#
# LICENSE
# <<

__author__ = 'blake.vandemerwe'

import logging
logger = logging.getLogger(__name__)

import time
from collections import OrderedDict

import gevent
from gevent import Greenlet, Timeout
from gevent.pool import Pool

DEFAULT_TIMEOUT = 30

class TaskTimeout(TimeoutError):
    pass

class TaskException(Exception):
    pass

class TaskKillException(TaskException):
    pass


class Task(object):
    def __init__(self,
                 name,
                 fn,
                 *args,
                 pool=None,
                 timeout=DEFAULT_TIMEOUT,
                 interval=None,
                 description=None,
                 **kwargs):

        self.name = name
        self.description = description
        self._error = None

        self._g = None
        self._value = None

        self.pool = pool
        self._fn = fn
        self._fn_args = args
        self._fn_kwargs = kwargs
        self._running = False

        self._timeout = None
        self.set_timeout(timeout)

        self.interval = interval
        self.schedule = False
        self._t_out = None
        self._runs = 0
        self._starts = 0
        self._last_runtime = 0
        self._total_runtime = 0

    def __make_greenlet(self):
        g = Greenlet(self._fn, self, *self._fn_args, **self._fn_kwargs)
        g.link(self._callback)
        return g

    def _callback(self, *args):
        duration = time.time() - self._starts
        self._t_out.cancel()
        self._g = None
        self._running = False
        self._last_runtime = duration
        self._total_runtime += duration
        if self.is_periodic and self.schedule:
            gevent.spawn_later(max(0, self.interval-duration), self.start)

    def start(self):
        if self.running:
            logger.warning('task.%s is already running' % self.name)
        elif self._g:
            logger.error('task.%s already running a greenlet' % self.name)
        else:
            self.schedule = True

        if not self.schedule:
            return

        if self._t_out:
            self._t_out.cancel()
            self._t_out = None

        self._t_out = Timeout(self._timeout, exception=TaskTimeout)
        self._t_out.start()

        self._starts = time.time()
        self._runs += 1

        try:
            g = self.__make_greenlet()

            self._g = g
            self.pool.start(g)
            self._running = True

        except TaskTimeout as t:
            self._error = t
            logger.warning('task.%s timeout: %s' % (self.name, t))
            self._callback()

        except Exception as e:
            logger.error('task.%s exception: ' % self.name)
            self._error = e
            raise e


    def stop(self, force=True):
        if self.running and self._g is not None:
            self._g.unlink(self._callback)
            if force:
                self._g.kill(exception=TaskKillException('task.%s forced stop'%self.name))
        self.schedule = False
        self._callback()

    def set_timeout(self, seconds):
        if isinstance(seconds, (int, float)):
            t = max(0.01, seconds)
            self._timeout = t

    def set_interval(self, seconds):
        if isinstance(seconds, (int, float)):
            t = max(0.01, seconds)
            self.interval = t

    @property
    def count(self):
        return self.runs

    @property
    def runs(self):
        return self._runs

    @property
    def running(self):
        if self.interval:
            return self._starts + self.interval > time.time()
        return self._running  # best guess

    @property
    def stopped(self):
        return not self.running

    @property
    def took(self):
        return self._last_runtime

    @property
    def every(self):
        return round(float(self.interval),2)

    @property
    def avg_runtime(self):
        return self._total_runtime / float(max(1, self.count))

    @property
    def is_periodic(self):
        return isinstance(self.interval, (int,float))

    def __repr__(self):
        return '<Task:%s(running=%s,runs=%d,every=%s)>' % (
            self.name, self.running, self.count, self.every)


class TaskPool(Pool):
    def __init__(self, size=None):
        super(TaskPool, self).__init__(size, Greenlet)

    @property
    def running_tasks(self):
        return self.size - self.free_count()

    @property
    def capacity(self):
        return round(1 - (self.free_count() / float(self.size)), 2) * 100


class TaskManager(object):
    def __init__(self, pool, *tasks):
        assert isinstance(pool, Pool)

        self.pool = pool

        self._tasks = OrderedDict()

        for task in tasks:
            self.add_tasks(task)

        if tasks:
            self.start_all()

    def __iter__(self):
        for t in self._tasks.values():
            yield t

    @property
    def tasks(self):
        return self._tasks

    def add_tasks(self, *t, and_start=True):
        for task in t:
            if not isinstance(task, Task):
                raise ValueError(task)
            if task.name in self._tasks.keys():
                raise KeyError(task.name)
            task.pool = self.pool
            self._tasks[task.name] = task
            if and_start and task.stopped:
                task.start()

    def start_task(self, name):
        t = self._tasks.get(name, None)
        if t:
            t.start()
        return t

    def stop_task(self, name, force=False):
        t = self._tasks.get(name, None)
        if t:
            t.stop(force=force)
        return t

    def start_all(self):
        for task in self:
            task.start()
        return self

    def stop_all(self, force=False):
        for task in self:
            task.stop(force=force)
        return self

    def remove_task_by(self, name=None, task=None):
        if name:
            t = self._tasks.pop(name, None)
            if t:
                t.stop()
        elif task:
            self.remove_task_by(name=task.name)

    def create_task(self, name, fn, *args, **kwargs):
        return Task(name, fn, self, *args, **kwargs)