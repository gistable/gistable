
import os
import sys

from kombu import Exchange, Queue
from datetime import timedelta
from config import cfg

import log

log.initLog(cfg.log)

sys.path.append(os.path.dirname(os.path.basename(__file__)))


_redis = cfg.redis
_email = cfg.email

REDIS_SERVER = "redis://:%s@%s:%d/%d" %(_redis['password'],_redis['host'],\
                                                    _redis['port'],_redis['db'])

BROKER_URL = REDIS_SERVER


BROKER_POOL_LIMIT = 200

BROKER_CONNECTION_TIMEOUT = 5
BROKER_CONNECTION_RETRY = True
BROKER_CONNECTION_MAX_RETRIES = 100

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600*12} # 12 hour

# BROKER_HEARTBEAT
# BROKER_HEARTBEAT_CHECKRATE


# Only AMQP broker support using ssl  
BROKER_USE_SSL = False 


CELERY_RESULT_BACKEND =REDIS_SERVER

CELERY_TIMEZONE = "Asia/Shanghai"

CELERY_TASK_RESULT_EXPIRES = 3600*24  # 1 day

CELERYD_CONCURRENCY = 6

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_CACHE_BACKEND = "memory"

CELERY_TASK_PUBLISH_RETRY = True
CELERY_TASK_PUBLISH_RETRY_POLICY = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 30,
    'interval_max': 60,
}


CELERYD_POOL = "processes"


CELERY_IMPORTS = (
    'tasks',
    'urlscan.tasks',
    'codescan.tasks',
    'webscan.tasks'
)


#################################################
#: Queue and Route related configuration
#################################################

CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'

CELERY_QUEUES = (
        Queue('errorhandler',Exchange('errorhandler'),routing_key='errorhandler'),
        Queue('urlscan.log',Exchange('urlscan.log'),routing_key='urlscan.log'),
        Queue('urlscan.spider',Exchange('urlscan.spider'),routing_key='urlscan.spider'),
        Queue('webscan',Exchange('webscan'),routing_key='webscan'),
        Queue('codescan',Exchange('codescan'),routing_key='codescan'),

    )



CELERY_ROUTES = ({
    'webscan.errorhandler': {
        'queue':'errorhandler',
        'routing_key':'errorhandler'
    }},

    {
    'webscan.urlscan.spider': {
        'queue': 'urlscan.spider',
        'routing_key': 'urlscan.spider'
    }},

    {
    'webscan.urlscan.logextract': {
        'queue': 'urlscan.log',
        'routing_key': 'urlscan.log'
    }},

    {
    'webscan.codescan': {
        'queue': 'codescan',
        'routing_key': 'codescan'
    }},

    {
    'webscan.webscan': {
        'queue': 'webscan',
        'routing_key': 'webscan'
    }},
)



#################################################
#: Events configuration, Event can be used for monitor by flower
#################################################
CELERY_SEND_EVENTS = True
CELERY_SEND_TASK_SENT_EVENT = True




#################################################
#: Log configuration
#################################################
CELERYD_HIJACK_ROOT_LOGGER = True
CELERYD_LOG_COLOR = True
CELERYD_LOG_FORMAT = "[%(asctime)s <%(processName)s>] %(levelname)s: %(message)s"
CELERYD_TASK_LOG_FORMAT = "[%(asctime)s <%(task_name)s %(task_id)s>] %(levelname)s: %(message)s"
CELERY_REDIRECT_STDOUTS = True





#################################################
#: E-mail configuration, Send mail to admin when task failed.
#################################################
CELERY_SEND_TASK_ERROR_EMAILS = True

ADMINS = (
    ("kenshin", "kenshin.acs@gmail.com"),
)

SERVER_EMAIL = _email['SERVER_EMAIL']

EMAIL_HOST = _email['EMAIL_HOST']
EMAIL_PORT = _email['EMAIL_PORT']
EMAIL_HOST_USER = _email['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = _email['EMAIL_HOST_PASSWORD']


