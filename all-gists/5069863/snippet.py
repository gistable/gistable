from time import time
from functools import wraps

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

class Metrics(object):
    def __init__(self, redis, keyspace='metrics'):
        self.db = redis
        self.keyspace = keyspace

    def incr(self, key):
        now = int(time())
        date_keys = [
            '%s:m%s' % (self.keyspace, now / MINUTE),
            '%s:h%s' % (self.keyspace, now / HOUR),
            '%s:d%s' % (self.keyspace, now / DAY),
        ]
        with self.db.map() as conn:
            for date_key in date_keys:
                conn.zincrby(date_key, key)

    def count(self, key):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                self.incr(key)
        return wrapped

from nydus.db import create_cluster

metrics = Metrics(create_cluster(
    'engine': 'nydus.db.backends.redis.Redis',
    'hosts': {0: {}},
), 'queue')

@metrics.count('task_name')
def my_task_name():
    pass