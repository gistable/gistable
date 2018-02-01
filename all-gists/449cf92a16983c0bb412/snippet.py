import socket

import redis


class RedisLock(object):
    """Redis Lock implementation over redis.StrictRedis.lock.

    :param strict_client: A StrictRedis client.
    :type strict_client: redis.StrictRedis.
    :param name: Key to use in redis.
    :type name: str
    :param owner: Lock's owner by default hostname.
    :type owner: str
    :param options: Options for redis.StrictRedis.lock
    :type options: dict

    """
    def __init__(self, strict_client, name, owner=None, **options): 
        self.name = name
        self._owner = None
        if self._owner is None:
            self._owner = socket.gethostname()
        self._auto_release = auto_release
        self._redis_client = strict_client
        self._lock = None
        self._lock_acquired = False
        self._options = options

    def __enter__(self):
        blocking = self._options.get('blocking', True)
        expire = self._options.get('expire', None)
        self.acquire(blocking=blocking, expire=expire)
        return self

    def __exit__(self, type_, value, tb):
        self.release()

    def acquire(self, blocking=True, expire=None):
        """Return whether the lock was acquired or not.

        :param blocking: If we should block or not while try to get the log.
        :type blocking: bool.
        :param expire: Second before the lock expires.
        :type expire: number

        :return: Flag indicating if the lock was acquired or not.
        :rtype: bool

        """
        self._lock = self._redis_client.lock(self.name, timeout=expire)
        self._lock_acquired = self._lock.acquire(blocking=blocking)
        return self._lock_acquired

    def release(self):
        """Return whether the lock was released or not.

        :return: Flag indicating if the lock was released or not.
        :rtype: bool

        """
        if self.acquired:
            self.lock.release()
            return True
        return False

    @property
    def owner(self):
        return self._owner

    @property
    def acquired(self):
        """Returns whether the lock is acquired or not."""
        return self._lock_acquired

    @property
    def lock(self):
        """Returns the redis.lock instance (low-level API)."""
        return self._lock


def some_work(obj_id, expire=3 * 60):
    key = 'some-work-{0}'.format(obj_id)
    lock_acquired = False

    redis_client = redis.StrictRedis()
    lock_manager = RedisLock(redis_client, key, expire=expire)
    try:
        lock_acquired = lock_manager.acquire(blocking=False)
        if lock_acquired:
            try:
                # Your code here
                do_work()
            except Exception:
                # Exception handling
        else:
            # Lock could not be acquired
    finally:
        lock_manager.release()


def some_work_with(obj_id, expire=3 * 60):
    key = 'some-work-{0}'.format(obj_id)

    redis_client = redis.StrictRedis()
    with RedisLock(redis_client, key, expire=expire) as lock:
        if lock.acquired:
            try:
                # Your code here
            except Exception:
                # Exception handling
        else:
            # Lock not acquired