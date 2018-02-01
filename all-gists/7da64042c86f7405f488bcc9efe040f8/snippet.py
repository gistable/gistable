import logging
import sys
from logging import config

# REF, modified from:
#   https://stackoverflow.com/a/19367225

if sys.platform == "darwin":
    address = '/var/run/syslog'
    facility = 'local1'
elif sys.platform == 'linux':
    address = '/dev/log'
else:
    address = ('localhost', 514)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            '%(asctime)s %(name)s %(levelname)-10s  %(message)s'
            },
        },
    'handlers': {
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'verbose',
            },
        'sys-logger0': {
            'class': 'logging.handlers.SysLogHandler',
            'address': address,
            'facility': "local0",
            'formatter': 'verbose',
            },
        },
    'loggers': {
        'sre_mon': {
            'handlers': ['sys-logger0', 'stderr'],
            'level': logging.DEBUG,
            'propagate': True,
            },
        }
    }


def main():
    config.dictConfig(LOGGING)
    logger = logging.getLogger('sre_mon')

    logger.debug("debugging...")
    logger.info("getting some info")
    logger.warning("Warning, Will Robinson!")
    logger.error("Error!")
    logger.critical("It's Critical")
