# Getting started:
# pip install python-json-logger

# settings.py
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(created)f %(exc_info)s %(filename)s %(funcName)s %(levelname)s %(levelno)s %(lineno)d %(module)s %(message)s %(pathname)s %(process)s %(processName)s %(relativeCreated)d %(thread)s %(threadName)s'
        },
        'verbose': {
            'format': 'levelname=%(levelname)s asctime=%(asctime)s module=%(module)s process=%(process)d thread=%(thread)d message="%(message)s"'
        }
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': '/path/to/logfile/application_name.log',
            'mode': 'a',
            # 10MB log file max
            'maxBytes': 10000000,
            # Original, plus 5 backups for 6 total log files
            'backupCount': 5
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL
        }
    }
}


try:
    from settingslocal import *
except ImportError:
    pass


# myapp.py
import settings
import logging

from logging import config

# Setup logging
config.dictConfig(settings.LOGGING)
 
logging.warning("Error occured while processing document",
                extra={"document_id": 1234, "user": "steve.exampleton@somewhere.org"} )
                
# Result:
"""
{  
   "asctime":"2016-01-28 17:05:28,717",
   "created":1454000728.717773,
   "exc_info":null,
   "filename":"myapp.py",
   "funcName":"test_a_logging_call",
   "levelname":"WARNING",
   "levelno":30,
   "lineno":10,
   "module":"myapp",
   "message":"Error occured while processing document",
   "pathname":"myapp.py",
   "process":15568,
   "processName":"MainProcess",
   "relativeCreated":25.239944458007812,
   "thread":140374777714496,
   "threadName":"MainThread",
   "user":"steve.exampleton@somewhere.org",
   "document_id":1234
}
"""