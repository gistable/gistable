CELERYD_HIJACK_ROOT_LOGGER = False


def setup_task_logger(logger=None, **kwargs):
    logger.propagate = 1

from celery import signals
signals.setup_logging.connect(lambda **kwargs: True)
signals.after_setup_task_logger.connect(setup_task_logger)
