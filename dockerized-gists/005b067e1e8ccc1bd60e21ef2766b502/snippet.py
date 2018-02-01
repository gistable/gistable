"""
License: MIT - https://opensource.org/licenses/MIT

ChromeLogger is a protocol which allows sending logging messages to the Browser.

This module implements simple support for Django. It consists of two components:

    * `LoggingMiddleware` which is responsible for sending all log messages
      associated with the request to the browser.
    * `ChromeLoggerHandler` a python logging handler which collects all messages.

Configuration in settings.py is as follows::

    MIDDLEWARE = [
        'chromelogger.LoggingMiddleware',
        ... # other middlewares
    ]

    LOGGING = {
        ...
        'handlers': {
            'browser': {
                'class': 'chromelogger.ChromeLoggerHandler',
            },
            ...
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'browser'],
                'level': 'DEBUG',
            },
            ...
        }
    }

"""
import json
import logging
import threading

HEADER_DATA = {
    'version': 1,
    'columns': ['log', 'backtrace', 'type'],
}

STORAGE = threading.local()


def map_level(level):
    """Maps a logging level to a string understood by browser devtools."""
    if level >= logging.ERROR:
        return 'error'
    elif level >= logging.WARNING:
        return 'warn'
    elif level >= logging.INFO:
        return 'info'
    return ''


def encode_data(data):
    """Return a base64 encoded json dump."""
    bytes = json.dumps(data).encode('utf-8').encode('base64').replace('\n', '')
    assert len(bytes) < 250 * 1024
    return bytes


class ChromeLoggerHandler(logging.Handler):
    def emit(self, record):
        try:
            STORAGE.records.append(record)
        except AttributeError:
            pass


def LoggingMiddleware(get_respone):
    def middleware(request):
        STORAGE.records = log_records = []

        try:
            response = get_respone(request)

            logging_data = HEADER_DATA.copy()
            rows = [
                [['{}:'.format(record.name), record.getMessage().strip()],
                '{} : {}'.format(record.pathname, record.lineno),
                map_level(record.levelno)]
                for record in log_records
            ]
            rows.insert(0, [
                ['{} request to {}'.format(request.method, request.get_full_path())],
                '', 'group'
            ])
            rows.append([[], '', 'groupEnd'])
            logging_data['rows'] = rows
            response['X-ChromeLogger-Data'] = encode_data(logging_data)
            return response

        finally:
            del STORAGE.records

    return middleware