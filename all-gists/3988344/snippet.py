class RedisCircularBuffer(object):

    def __init__(self, namespace, size):
        self.namespace = namespace
        self.size = size
        import redis
        self.redis = redis.Redis()

    def append(self, item):
        self.redis.lpush(self.namespace, item)
        self.redis.ltrim(self.namespace, 0, self.size)

    def __iter__(self):
        return (x for x in self.redis.lrange(self.namespace, 0, self.size))

    def __len__(self):
        return self.redis.llen(self.namespace)

    def __repr__(self):
        return '[' + ','.join(
            repr(x) for x in self
        ) + ']'
