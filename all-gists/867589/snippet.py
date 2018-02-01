import unittest, os, os.path, sys, urllib
import tornado.database
import tornado.options
from tornado.options import options
from tornado.testing import AsyncHTTPTestCase

# add application root to sys.path
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(APP_ROOT, '..'))

# import your app module
import your.app

# Create your Application for testing
# In this example, the tornado config file is located in: APP_ROOT/config/test.py
tornado.options.parse_config_file(os.path.join(APP_ROOT, 'config', 'test.py'))
app = your.app.Application()

# convenience method to clear test database
# In this example, we simple reapply APP_ROOT/db/schema.sql to test database
def clear_db(app=None):
    os.system("mysql %s < %s" % (options.mysql_database, os.path.join(APP_ROOT, 'db', 'schema.sql')))

# Create your base Test class.
# Put all of your testing methods here.
class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        clear_db()
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return app      # this is the global app that we created above.

    def get_http_port(self):
        return options.port


# Your TestHandler class
# They are runnable via nosetests as well.
class TestBucketHandler(TestHandlerBase):
    def create_something_test(self):

        # Example on how to hit a particular handler as POST request.
        # In this example, we want to test the redirect,
        # thus follow_redirects is set to False
        post_args = {'email': 'bro@bro.com'}
        response = self.fetch(
            '/create_something',
            method='POST',
            body=urllib.urlencode(post_args),
            follow_redirects=False)

        # On successful, response is expected to redirect to /tutorial
        self.assertEqual(response.code, 302)
        self.assertTrue(
            response.headers['Location'].endswith('/tutorial'),
            "response.headers['Location'] did not ends with /tutorial"
        )
