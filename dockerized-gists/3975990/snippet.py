from sentry.conf.server import *
import os.path

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        # You can swap out the engine for MySQL easily by changing this value
        # to ``django.db.backends.mysql`` or to PostgreSQL with
        # ``django.db.backends.postgresql_psycopg2``
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sentry_server',
        'USER': 'sentry',
        'PASSWORD': '****',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    }
}

SENTRY_KEY = '***********'

# Set this to false to require authentication
SENTRY_PUBLIC = False

# You should configure the absolute URI to Sentry. It will attempt to guess it if you don't
# but proxies may interfere with this.
# SENTRY_URL_PREFIX = 'http://sentry.example.com'  # No trailing slash!
SENTRY_URL_PREFIX = 'http://sentry.sistemas.pdg.com.br'

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    'workers': 3,  # the number of gunicorn workers
    # 'worker_class': 'gevent',
}

# Mail server configuration

# For more information check Django's documentation:
#  https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = '192.168.4.71'
EMAIL_HOST_USER = ''  # 'sistemas'
EMAIL_HOST_PASSWORD = ''  # '***'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
SENTRY_EMAIL_SUBJECT_PREFIX = '[Sentry] '
import logging
SENTRY_MAIL_LEVEL = logging.DEBUG


ADMINS=()
SENTRY_ADMINS=('felipe.rafael@pdg.com.br')
SENTRY_SERVER_EMAIL='sistemas@pdg.com.br'


BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "sentry"
BROKER_USER = "sentry"
BROKER_PASSWORD = "****"

SENTRY_USE_QUEUE = (
    'sentry.tasks.cleanup.cleanup',
    'sentry.tasks.post_process.post_process_group',
    'sentry.tasks.process_buffer.process_incr',
)

SENTRY_BUFFER = 'sentry.buffer.base.Buffer'
SENTRY_BUFFER_OPTIONS = {
    'hosts': {
        0: {
            'host': 'localhost',
            'port': 6379
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.CacheClass',
        'LOCATION': '127.0.0.1:11211'
    }
}
SENTRY_CACHE_BACKEND = 'default'

DEBUG=True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': ['sentry'],
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'mail_admins': {
            'level': 'DEBUG',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
