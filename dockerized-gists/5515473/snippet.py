DEBUG=True
LOG_FILE_SIZE=1024*1000

LOGGING = {
    'version' : 1,
    'disable_existing_loggers':True,
    'formatters' : {
        'simple' : {
            'format' : '%(levelname)s %(name)s %(message)s'
        },
        'errors' : {
            'format' : '%(levelname)s %(asctime)s %(name)s %(message)s \n  View: %(view)s \n  Login_id: %(login_id)s \n  GET:\n%(parameters)s'
        },
        'precise' : {
            'format' : '%(levelname)s %(asctime)s %(name)s %(message)s'
        },
        'timing': {
            'format' : '%(asctime)-15s %(message)s'
        },
        'sourcetrace': {
            'format': '-'*80 + '\n%(sql)s\n\nStacktrace of SQL query producer:\n%(sourcetrace)s' + '-'*80 + '\n'
        },
    },
    'handlers' : {
        'null' : {
            'level' : 'DEBUG',
            'class' : 'django.utils.log.NullHandler'
        },
        'console' : { 'class' : 'logging.StreamHandler' , 'formatter' : 'simple'},
        'timing-file' : { 'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : 'api-timing.log',
            'formatter' : 'timing',
            'backupCount' : 10,
            'maxBytes' : LOG_FILE_SIZE
        },
        'django.db.sourcetrace': {
            'class': 'logging.StreamHandler',
            'formatter': 'sourcetrace'
        },
    },
    'root' : {
        'level' : 'DEBUG',
        'handlers' : ['console']
    },
    'loggers' : {
        'django': {
            'handlers' : ['console'],
            'propagate': False,
            'level' : 'DEBUG'
        },
        'timing': {
            'propagate': False,
            'level' : 'DEBUG',
            'handlers' : ['timing-file']
        },
        'django.db.backends': {
            'handlers': ['django.db.sourcetrace'],
            'propagate': False,
            'level': 'DEBUG'
        }
    }
}


import logging, inspect

class ContextFilter(logging.Filter):
    """
    Injects stack trace information when added as a filter to a
    python logger
    """

    def filter(self, record):
        source_trace = ''

        stack = inspect.stack()
        for s in reversed(stack):
            line = s[2]
            file = '/'.join(s[1].split('/')[-3:])
            calling_method = s[3]
            source_trace += '%s in %s at %s\n' % (line, file, calling_method)

        # pass to format string
        record.sourcetrace = source_trace

        # clean up
        del stack

        return True

django_db_backends_logger = logging.getLogger('django.db.backends')
f = ContextFilter()
django_db_backends_logger.addFilter(f)

