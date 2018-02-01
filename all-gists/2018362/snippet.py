"""Decorator to quickly add statsd (graphite) instrumentation to Celery
task functions.

With some slight modification, this could be used to instrument just
about any (non-celery) function and be made abstract enough to customize
metric names, etc.

Stats reported include number of times the task was accepted by a worker
(`started`), the number of successes, and the number of times the task
raised an exception. In addition, it also reports how long the task took
to complete. Usage:

>>> @task
>>> @instrument_task
>>> def mytask():
>>>     # do stuff
>>>     pass

Please note that the order of decorators is important to Celery. See
http://ask.github.com/celery/userguide/tasks.html#decorating-tasks
for more information.

Uses `simple_decorator` from
http://wiki.python.org/moin/PythonDecoratorLibrary#Property_Definition

Limitation: Does not readily work on subclasses of celery.tasks.Task
because it always reports `task_name` as 'run'
"""

# statsd instrumentation
from celery import current_app
import statsd

@simple_decorator
def instrument_task(func):
    """Wraps a celery task with statsd instrumentation code"""

    def instrument_wrapper(*args, **kwargs):
        stats_conn = statsd.connection.Connection(
            host = current_app.conf['STATSD_HOST'],
            port = current_app.conf['STATSD_PORT'],
            sample_rate = 1)

        task_name = func.__name__

        counter = statsd.counter.Counter('celery.tasks.status',stats_conn)
        counter.increment('{task_name}.started'.format(**locals()))

        timer = statsd.timer.Timer('celery.tasks.duration', stats_conn)
        timer.start()

        try:
            ret = func(*args, **kwargs)
        except:
            counter.increment('{task_name}.exceptions'.format(**locals()))
            raise
        else:
            counter.increment('{task_name}.success'.format(**locals()))
            timer.stop('{task_name}.success'.format(**locals()))
            return ret
        finally:
            try:
                del timer
                del counter
                del stats_conn
            except:
                pass

    return instrument_wrapper

def simple_decorator(decorator):
    """Borrowed from:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Property_Definition

    Original docstring:
    This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied."""
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__module__ = f.__module__ # or celery throws a fit
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

