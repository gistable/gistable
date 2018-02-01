#!/usr/bin/env python
# encoding: utf-8

from selenium import webdriver
import unittest
import nose
from nose.plugins.multiprocess import MultiProcess
import new
import json
import httplib
import base64

chosen_browsers = [
    ('XP', 'internet explorer', '6'),
    ('XP', 'internet explorer', '7'),
    ('XP', 'internet explorer', '8'),
    ('VISTA', 'internet explorer', '9'),
    ('VISTA', 'firefox', '11'),
    # for Se1 platforms are a big different
    #('Windows 2003', 'iexplore', '6'),
    #('Windows 2003', 'iexplore', '7'),
    #('Windows 2003', 'iexplore', '8'),
    #('Windows 2008', 'iexplore', '9'),
    #('Windows 2008', 'firefox', '11'),
]

user = "your-sauce-username"
key = "your-sauce-access-key"

class ManualTest(unittest.TestCase):
    # Nose won't run the original Test Class, we'll change this in the
    # dynamically generated classes
    __test__ = False

    def setUp(self):
        des_caps = {
                # The following properties are set dynamically
                'platform': self.os,
                'browserName': self.br,
                'version': self.version,
                'name': self.name,
                }
        # instantiate the browser
        self.driver = webdriver.Remote(desired_capabilities=des_caps,
                                       command_executor="http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
                                       % (user, key))
        # this is just handy
        self.driver.implicitly_wait(10)

        # Se1 is just a few changes
        #des_caps['username'] = user
        #des_caps['access-key'] = key
        #des_caps['os'] = des_caps.pop('platform')
        #des_caps['browser'] = des_caps.pop('browserName')
        #des_caps['browser-version'] = des_caps.pop('version')
        #self.browser = selenium(
        #    'ondemand.saucelabs.com',
        #    '80',
        #    json.dumps(des_caps),
        #    'http://saucelabs.com')
        #self.browser.start()
        #self.browser.set_timeout(900000)

    def test_basic_page(self):
        self.driver.get("http://saucelabs.com/about/team")
        assert 'Sauce' in self.driver.title

    def report_pass_fail(self):
        # Sauce doesn't really know what the test in your end does with the
        # browser, let us know
        base64string = base64.encodestring('%s:%s' % (user, key))[:-1]
        result = json.dumps({'passed': self._exc_info() == (None, None, None)})
        connection = httplib.HTTPConnection('saucelabs.com')
        connection.request('PUT', '/rest/v1/%s/jobs/%s' % (user,
                                                           self.driver.session_id),
                           result,
                           headers={"Authorization": "Basic %s" % base64string})
        result = connection.getresponse()
        return result.status == 200

    def tearDown(self):
        self.report_pass_fail()
        self.driver.quit()

# Here's where the magic happens
classes = {}
for os, browser, version in chosen_browsers:
    # Make a new class name for the actual test cases
    name = "%s_%s_%s_%s" % (ManualTest.__name__, os, browser, version)
    name = name.encode('ascii')
    if name.endswith("."): name = name[:-1]
    for x in ".-_":
        name = name.replace(x, " ")

    # Copy the magic __dict__ from the original class
    d = dict(ManualTest.__dict__)
    # Update the new class' dict with a new name and a __test__ == True
    d.update({'__test__': True,
              '__name__': name,
              # Set these properties dynamically, the test uses them to
              # instantiate the browser
              'name': name,
              'os': os,
              'br': browser,
              'version': version,
             })

    # append the new class to the classes dict
    classes[name] = new.classobj(name, (ManualTest,), d)

# update the global context (believe it or not, it's a dict), with the new
# classes we just dynamically generated
globals().update(classes)

# this is just handy. If __main__, just run the tests in multiple processes
if __name__ == "__main__":
    nose.core.run(argv=["nosetests", "-vv",
                        "--processes", len(chosen_browsers),
                        "--process-timeout", 180,
                        __file__],
                  plugins=[MultiProcess()])
