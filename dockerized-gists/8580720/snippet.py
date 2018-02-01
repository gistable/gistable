import threading
import logging
from functools import wraps


logger = logging.getLogger(__name__)


def timeout(secs=None):
    def my_decorator(target, *args, **kwargs):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=target, args=args, kwargs=kwargs)
            t.start()
            returned_value = t.join(secs)
            if t.is_alive():
                logger.warning('Timeout in thread running {}'.format(target))
            return returned_value
        return wraps(target)(wrapper)
    return my_decorator