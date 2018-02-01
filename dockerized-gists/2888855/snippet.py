"""

    Pyramid + SQLAlchemy + PostgreSQL + Selenium test combo example.

    Mikko Ohtamaa

    http://opensourcehacker.com

    If you get::

            Traceback (most recent call last):
          File "alphadog/tests/test_selenium_render.py", line 63, in <module>
            setUpModule()
          File "alphadog/tests/test_selenium_render.py", line 44, in setUpModule
            browser = webdriver.Firefox(firefox_profile=profile)
          File "/Users/moo/code/xxx-base/venv/lib/python2.7/site-packages/selenium-2.7.0-py2.7.egg/selenium/webdriver/firefox/webdriver.py", line 46, in __init__
            self.binary, timeout),
          File "/Users/moo/code/xxx-base/venv/lib/python2.7/site-packages/selenium-2.7.0-py2.7.egg/selenium/webdriver/firefox/extension_connection.py", line 46, in __init__
            self.binary.launch_browser(self.profile)
          File "/Users/moo/code/xxx-base/venv/lib/python2.7/site-packages/selenium-2.7.0-py2.7.egg/selenium/webdriver/firefox/firefox_binary.py", line 44, in launch_browser
            self._wait_until_connectable()
          File "/Users/moo/code/xxx-base/venv/lib/python2.7/site-packages/selenium-2.7.0-py2.7.egg/selenium/webdriver/firefox/firefox_binary.py", line 87, in _wait_until_connectable
            raise WebDriverException("Can't load the profile. Profile Dir : %s" % self.profile.path)
        selenium.common.exceptions.WebDriverException: Message: "Can't load the profile. Profile Dir : /var/folders/O8/O8pt7q52F7Oi+P3O0pNqq++++TI/-Tmp-/tmp74FwCp"


    ...Selenium Python package update most likely needed (Firefox is too new).

"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import threading
import time
import unittest
from wsgiref.simple_server import make_server
from urlparse import urlparse

#from pyramid import testing
from webtest import TestApp

from selenium import webdriver

#: The URL where WSGI server is run from where Selenium browser loads the pages
HOST_BASE = "http://localhost:8521"


class ServerThread(threading.Thread):
    """ Run WSGI server on a background thread.

    Pass in WSGI app object and serve pages from it for Selenium browser.
    """

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.srv = None

    def run(self):
        """
        Open WSGI server to listen to HOST_BASE address
        """
        parts = urlparse(HOST_BASE)
        domain, port = parts.netloc.split(":")
        self.srv = make_server(domain, int(port), self.app)
        try:
            self.srv.serve_forever()
        except:
            import traceback
            traceback.print_exc()
            # Failed to start
            self.srv = None

    def quit(self):
        """
        """
        if self.srv:
            self.srv.shutdown()


class TestRenderShow(unittest.TestCase):
    """
    Test the rendering page try Selenium
    """

    @classmethod
    def setUpClass(cls):
        """
        Create a Firefox test browser instance with hacked settings.

        We do this only once per testing module.
        """

        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        cls.browser = webdriver.Firefox(firefox_profile=profile)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def setUpPostgreSQL(cls):
        """
        Set-up PostgreSQL database
        """

    def setUp(self):
        """
        Set up WSGI app, server and clear PostgreSQL database.
        """

        # Set up our Pyramid app
        from alphadog.config.main import main

        # Spoofed Paster style .ini config
        settings = {

            # Explcitly pass in PostreSQL database prepared by hand beforehand.
            # This database is used for testing and cleared from the rows
            # at the beginning of each test.
            # To initialize:
            # python dbmanage.py selenium.ini version_control
            # python dbmanage.py selenium.ini upgrade
            'sqlalchemy.url': 'postgresql://xxx-dev@localhost:5432/xxx-tests',

            # Set our Selenium testing flag to True
            # (will configure additional views)
            'selenium': "true",

            # No email output in any case
            'mail.on': "false",
        }

        app = main({}, **settings)

        self.server = ServerThread(app)
        self.server.start()

        # Wait randomish time to allows SocketServer to initialize itself
        time.sleep(0.3)

        self.assertNotEqual(self.server.srv, None, "Failed to start the test web server")

        self.app = TestApp(app)

        self.nukePostgres()

    def nukePostgres(self):
        """
        Purge PSQL database by deleting all objects
        """
        from alphadog.models import DBSession
        from alphadog.models import Show
        session = DBSession()
        session.query(Show).delete()

    def tearDown(self):
        """
        Take down the server.
        """
        self.server.quit()

    def test_render_default(self):
        """
        xxx: render pages and use Selenium to poke them
        """
        # Available Selenium API calls:
        # http://code.google.com/p/selenium/source/browse/trunk/py/selenium/webdriver/remote/webdriver.py

        # Open the page
        page = "/test_render_show_with_two_images/"
        self.browser.get(HOST_BASE + page)

        # XXX: Bang Selenium here...
