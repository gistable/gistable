from functools import wraps, update_wrapper

class Task(object):
    """
Class that wraps a function to enqueue in pyres
"""
    _resque_conn = None

    def __init__(self, func, priority):
        self.func = func
        self.priority = priority

        # Allow this class to be called by pyres
        self.queue = str(priority)
        self.perform = func

        # Wrap func
        update_wrapper(self, func)

    # _resque wraps the underlying resque connection and delays initialisation
    # until needed
    @property
    def _resque(self):
        if self._resque_conn is None:
            from background import connections
            self._resque_conn = connections.get_resque_connection()
        return self._resque_conn

    @_resque.setter
    def _resque(self, val):
        self._resque_conn = val

    def enqueue(self, *args, **kwargs):
        self.enqueue_with_priority(self.priority, *args, **kwargs)

    def enqueue_with_priority(self, priority, *args, **kwargs):
        if kwargs:
            raise Exception('Cannot pass kwargs to enqueued tasks')
        class_str = '%s.%s' % (self.__module__, self.__name__)
        self._resque.enqueue_from_string(class_str, str(priority), *args)

    def enqueue_at(self, dt, *args, **kwargs):
        self.enqueue_at_with_priority(dt, self.priority, *args, **kwargs)

    def enqueue_at_with_priority(self, dt, priority, *args, **kwargs):
        if kwargs:
            raise Exception('Cannot pass kwargs to enqueued tasks')
        class_str = '%s.%s' % (self.__module__, self.__name__)
        self._resque.enqueue_at_from_string(dt, class_str, str(priority), *args)

    def enqueue_delay(self, td, *args, **kwargs):
        self.enqueue_delay_with_priority(td, self.priority, *args, **kwargs)

    def enqueue_delay_with_priority(self, td, priority, *args, **kwargs):
        dt = datetime.now() + td
        self.enqueue_at_with_priority(dt, priority, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return 'Task(func=%s, priority=%s)' % (self.func, self.priority)

def task(priority, cls=Task):
    def _task(f):
        return cls(f, priority)
    return _task