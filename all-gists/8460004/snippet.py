"""
This module adds Redis Sentinel transport support to Celery.
Current version of celery doesn't support Redis sentinel client, which is must have for automatic failover.

To use it::

    import register_celery_alias
    register_celery_alias("redis-sentinel")

    celery = Celery(..., broker="redis-sentinel://...", backend="redis-sentinel://...")
"""
from celery.backends import BACKEND_ALIASES
from kombu.transport import TRANSPORT_ALIASES
from celery.backends.redis import RedisBackend
from kombu.utils import cached_property
from kombu.transport.redis import Transport, Channel
from redis import Redis
from redis.sentinel import Sentinel


class RedisSentinelBackend(RedisBackend):

    def __init__(self, sentinels=None, sentinel_timeout=None, socket_timeout=None,
                 min_other_sentinels=0, service_name=None, **kwargs):
        super(RedisSentinelBackend, self).__init__(**kwargs)
        conf = self.app.conf

        def _get(key):
            try:
                return conf['CELERY_REDIS_SENTINEL_%s' % key]
            except KeyError:
                pass

        self.sentinels = sentinels or _get("SENTINELS")
        self.sentinel_timeout = sentinel_timeout or _get("SENTINEL_TIMEOUT")
        self.socket_timeout = socket_timeout or _get("SOCKET_TIMEOUT")
        self.min_other_sentinels = min_other_sentinels or _get("MIN_OTHER_SENTINELS")
        self.service_name = service_name or _get("SERVICE_NAME")

    @cached_property
    def client(self):
        sentinel = Sentinel(self.sentinels, min_other_sentinels=self.min_other_sentinels,
                            password=self.password, sentinel_kwargs={"socket_timeout": self.sentinel_timeout})
        return sentinel.main_for(self.service_name, redis_class=Redis, socket_timeout=self.socket_timeout)


class SentinelChannel(Channel):

    from_transport_options = Channel.from_transport_options + (
        "service_name",
        "sentinels",
        "password",
        "min_other_sentinels",
        "sentinel_timeout",
    )

    #noinspection PyUnresolvedReferences
    @cached_property
    def _sentinel_managed_pool(self):

        sentinel = Sentinel(
            self.sentinels,
            min_other_sentinels=getattr(self, "min_other_sentinels", 0),
            password=getattr(self, "password", None),
            sentinel_kwargs={"socket_timeout": getattr(self, "sentinel_timeout", None)},
        )
        return sentinel.main_for(self.service_name, self.Client,
                                   socket_timeout=self.socket_timeout).connection_pool

    def _get_pool(self):
        return self._sentinel_managed_pool


class RedisSentinelTransport(Transport):
    Channel = SentinelChannel


def register_celery_alias(alias="redis-sentinel"):
    BACKEND_ALIASES[alias] = "utils.celery_sentinel.RedisSentinelBackend"
    TRANSPORT_ALIASES[alias] = "utils.celery_sentinel.RedisSentinelTransport"
