# encoding: utf8
from jinja2 import BytecodeCache
from config import TEMPLATE_CACHE_PREFIX, TEMPLATE_CACHE_TTL


class RedisTemplateBytecodeCache(BytecodeCache):
    '''Implements a Jinja2 bytecode cache on top of a pyredis.StrictRedis
    connection
    See: http://jinja.pocoo.org/docs/api/#bytecode-cache
    '''

    def __init__(self, redis_cnx):
        self.cnx = redis_cnx

    def key(self, k):
        return '%s_%s' % (TEMPLATE_CACHE_PREFIX, k)

    def load_bytecode(self, bucket):
        bc = self.cnx.get(self.key(bucket.key))
        if bc:
            bucket.load_bytecode(bc)

    def dump_bytecode(self, bucket):
        self.cnx.setex(
            self.key(bucket.key),
            TEMPLATE_CACHE_TTL,
            bucket.bytecode_to_string()
        )

    def clear(self):
        pass
