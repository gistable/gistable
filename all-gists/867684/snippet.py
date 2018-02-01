import unittest, os, os.path, sys
import tornado.database
import tornado.options
from tornado.options import options

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(APP_ROOT, '..'))

# import your model module
import your.model as model

# import your app module
from your.app import *

# convenience method to clear test database
# In this example, we simple reapply APP_ROOT/db/schema.sql to test database
def clear_db(app=None):
    os.system("mysql %s < %s" % (options.mysql_database, os.path.join(APP_ROOT, 'db', 'schema.sql')))


# Global App for testing
tornado.options.parse_config_file(os.path.join(APP_ROOT, 'config', 'test.py'))
app = Application()

# In this example, we have a model called Link and we want to test it.
class TestLink(unittest.TestCase):
    def setUp(self):
        clear_db()
        self.bucket = app.bucket
        self.link = app.link

    # Testing INSERT
    def save_to_test(self):
        sha = 'lol'
        self.link.save_to(sha, "http://cooln.es")
        self.assertEqual(len(self.link.all_by_sha(sha)), 1)

    # testing SELECT
    def all_by_sha_test(self):
        sha = 'lol'
        link_id = self.link.save_to(sha, "http://cooln.es")
        self.assertTrue(link_id is not None)

        link_id = self.link.save_to(sha, "http://tornadoweb.org")
        self.assertTrue(link_id is not None)

        self.assertEqual(len(self.link.all_by_sha(sha)), 2)
