#coding: utf-8
from django.test.simple import DjangoTestSuiteRunner
from nose.plugins.skip import SkipTest

from mongoengine.python_support import PY3
from mongoengine import connect

try:
    from django.test import TestCase
    from django.conf import settings
except Exception as err:
    if PY3:
        from unittest import TestCase
        # Dummy value so no error
        class settings:
            MONGO_DATABASE_NAME = 'dummy'
    else:
        raise err

class MongoTestRunner(DjangoTestSuiteRunner):
    """
        A test runner that can be used to create, connect to, disconnect from, 
        and destroy a mongo test database for standard django testing.

        NOTE:
            The MONGO_PORT and MONGO_DATABASE_NAME settings must exist, create them
            if necessary.
        
        REFERENCE:
            http://nubits.org/post/django-mongodb-mongoengine-testing-with-custom-test-runner/
    """

    mongodb_name = 'test_%s' % (settings.MONGO_DATABASE_NAME, )

    def setup_databases(self, **kwargs):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name, port=settings.MONGO_PORT)
        print 'Creating mongo test database ' + self.mongodb_name
        return super(MongoTestRunner, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        print 'Dropping mongo test database: ' + self.mongodb_name
        disconnect()
        super(MongoTestRunner, self).teardown_databases(old_config, **kwargs)
