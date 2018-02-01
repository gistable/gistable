# -*- coding: utf-8 -*-
"""
Extremely fast Django test runner, based on the idea that your database schema
and fixtures are changed much more seldom that your code and tests.  All you
need is to make sure that your "quickstart.sqlite" database file is always up
to date.

BEWARE: Don't run this test runner on production server. It assumes that you 
use only one database configured as "default", and its db engine is SQLite.
Otherwise your tests can eat your data!

How to use it:

1. Make sure that APSW (another python SQLite wrapper) is installed. Usually
   it's enough to say:

    apt-get install python-apsw

2. Include this file somewhere in your project

3. Create database alias named "quickstart" with sqlite3 backend in your
   settings.py:

    DATABASES = {
         ..
        'quickstart': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '.../quickstart.sqlite',
        },
    }

4. Type ./manage.py syncdb --database quickstart once and make sure that file
   "quickstart.sqlite" has appeared

5. Redefine variable TEST_RUNNER in the settings.py .

    TEST_RUNNER = 'yourproject.yourapp.tests.runner.TestSuiteRunner'

6. Run a single test and be amazed how fast it is now.

If your schema and/or fixtures have changed, just remove quickstart.sqlite and
recreate it with syncdb command.
"""
import apsw
from django.test.simple import DjangoTestSuiteRunner
from django.db import connections

class TestSuiteRunner(DjangoTestSuiteRunner):

    def setup_databases(self, **kwargs):
        quickstart_connection = connections['quickstart']
        quickstart_dbname = quickstart_connection.settings_dict['NAME']
        
        memory_connection = apsw.Connection(':memory:')
        quickstart_connection = apsw.Connection(quickstart_dbname)
        with memory_connection.backup('main', quickstart_connection, 'main') as backup:
            while not backup.done:
                backup.step(100)
                
        connection = connections['default']
        connection.settings_dict['NAME'] = memory_connection
        cursor = connection.cursor()

    def teardown_databases(self, old_config, **kwargs):
        pass