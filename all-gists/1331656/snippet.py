LOGGLY_INPUT_KEY = "your key here"

import hoover
import logging

def initialize_loggly(loglevel=logging.WARN, **kwargs):
    handler = hoover.LogglyHttpHandler(token=LOGGLY_INPUT_KEY)
    log = logging.getLogger('celery')
    log.addHandler(handler)
    log.setLevel(loglevel)
    return log

from celery.signals import setup_logging
setup_logging.connect(initialize_loggly)
