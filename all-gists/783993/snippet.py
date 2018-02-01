import mongoengine
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

class MongoEngineConnectionMiddleware(object):
    ''' Ensure that a separate mongoengine connection is made per thread.
        See: http://groups.google.com/group/mongoengine-users/browse_thread/thread/1aa3f9d65627c04

        Assumes the following is your Django settings. Tweak as needed.
        MONGODB = {
            'db': '<database_name>',
            'options': {
                'host': '<host>',
                'port': <port>,
                'username': '<username>',
                'password': '<password>'
                }
            }
    '''
    def __init__(self):
        mongoengine.connect(settings.MONGODB['db'], **settings.MONGODB['options'])
        raise MiddlewareNotUsed