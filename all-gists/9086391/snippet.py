"""

Simple view decorator for flask and mongoengine/pymongo to auto-retry with delay on
pymongo.errors.AutoReconnect exception.

"""
from functools import wraps
import time
from pymongo.errors import AutoReconnect
import flask
from werkzeug.exceptions import InternalServerError


def retry_on_reconnect_error(retry_count=2, exponential_delay=False):
    """
    Automatic retry on PyMongo AutoReconnect exceptions.
    Inspired by http://www.arngarden.com/2013/04/29/handling-mongodb-autoreconnect-exceptions-in-python-using-a-proxy/
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if retry_count < 1:
                raise ValueError(u"retry_count must be 1 or higher.")
            for i in xrange(retry_count):
                try:
                    flask.current_app.logger.debug('trying db request %s', f)
                    v = f(*args, **kwargs)
                    flask.current_app.logger.debug('db request %s success', f)
                    return v
                except AutoReconnect as e:
                    if exponential_delay:
                        method = u"exponential"
                        delay = pow(2, i)
                    else:
                        method = u"simple"
                        delay =.1

                    flask.current_app.logger.warn(u'Transient error %s (retry #%d)'
                                                  ', method=%s sleeping %f',
                                                  e,
                                                  i+1,
                                                  method,
                                                  delay)
                    time.sleep(delay)
            msg = u'AutoReconnect retry failed.'
            flask.current_app.logger.error(msg)
            raise InternalServerError(description=msg)
        return decorated_function
    return decorator