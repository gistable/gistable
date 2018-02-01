LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        },
    },
    'handlers': {
       'fluentinfo':{
            'level':'INFO',
            'class':'fluent.handler.FluentHandler',
            'formatter': 'verbose',
            'tag':'app.info',
            'host':'localhost',
            'port':24224,
            # 'timeout':3.0,
            # 'verbose': False
        },
       'fluentdebug':{
            'level':'DEBUG',
            'class':'fluent.handler.FluentHandler',
            'formatter': 'verbose',
            'tag':'app.debug',
            'host':'localhost',
            'port':24224,
            # 'timeout':3.0,
            'verbose': True
        },
    },
    'loggers': {
        'app.debug': {
            'handlers': ['fluentdebug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app.info': {
            'handlers': ['fluentinfo'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}