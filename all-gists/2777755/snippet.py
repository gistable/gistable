DEV_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'main_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(LOG_PATH, 'main.log'),
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(LOG_PATH, 'error.log'),
        },
        'requests_main_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(LOG_PATH, 'requests_main.log'),
        },
        'requests_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(LOG_PATH, 'requests_error.log'),
        }
    },
    'loggers': {
        'foo.bar': {
            'handlers': ['console', 'main_file', 'error_file'],
            'level': 'DEBUG',
            'propogate': False
        },
    },
    'root': {
        'handlers': ['console', 'main_file', 'error_file'],
        'level': 'DEBUG',
    }
}

# no console ouptput
PROD_LOGGING = DEV_LOGGING.copy()
PROD_LOGGING.update({
    'loggers': {
        'foo.bar': {
            'handlers': ['main_file', 'error_file'],
            'level': 'DEBUG',
            'propogate': False
        },
    },
    'root': {
        'handlers': ['main_file', 'error_file'],
        'level': 'DEBUG',
    }
})