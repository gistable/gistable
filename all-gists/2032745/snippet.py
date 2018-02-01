# java -cp ~/Downloads/Sikuli-X-1.0rc3\ \(r905\)-linux-x86_64/Sikuli-IDE/sikuli-script.jar org.python.util.jython test.py
from __future__ import with_statement
import unittest

from sikuli.Sikuli import *


class Firefox(object):
    """
    very simple firefox browser context manager
    """

    def __init__(self, url):
        self.url = url

    def __enter__(self):
        Screen(0)
        app = App.open('firefox')
        wait(2)
        type('l', KEY_CTRL)
        type("%s\n" % self.url)

    def __exit__(self, type_, value, traceback):
        type('q', KEY_CTRL)


class TestBasicScenario(unittest.TestCase):
    """
    + check the existence of the download overlay and the toggling of its
    visibility with the visiblity of the customer list
    + edit, delete and save (undelete) of a customer yaml (basic scenario)
    """

    def test_01_on_index_download_overlay_visible(self):
        assert exists("download-overlay.png")

    def test_02_click_settings_overlay_disappera(self):
        click("settings.png")
        wait("new-customer.png" )
        assert not exists("download-overlay.png")

    def test_03_edit_customer(self):
        click("semansarada.png")
        wait("semansarada-editing.png")
        assert exists("semansarada-yaml.png")

    def test_04_deleting_customer(self):
        click("trash.png")
        wait("semansarada-deleted.png")

    def test_05_undeleting_customer(self):
        click("semansarada.png")
        wait("semansarada-editing.png")
        click("save.png")
        wait("semansarada-saved.png")

    def test_06_closing_customer_list(self):
        click("settings.png")
        assert exists("download-overlay.png")


# Sikuli settings (no logs)
Settings.ActionLogs = False
Settings.InfoLogs = False
Settings.DebugLogs = False

with Firefox('http://localhost:3000'):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicScenario)
    unittest.TextTestRunner(verbosity=2).run(suite)

"""
[eugene]~/Code/sikuli/tollbooth.sikuli$ java -cp ~/Downloads/Sikuli-X-1.0rc3\ \(r905\)-linux-x86_64/Sikuli-IDE/sikuli-script.jar org.python.util.jython test.py
[info] Sikuli vision engine loaded.
[info] VDictProxy loaded.
test_01_on_index_download_overlay_visible (__main__.TestBasicScenario) ... ok
test_02_click_settings_overlay_disappera (__main__.TestBasicScenario) ... ok
test_03_edit_customer (__main__.TestBasicScenario) ... ok
test_04_deleting_customer (__main__.TestBasicScenario) ... ok
test_05_undeleting_customer (__main__.TestBasicScenario) ... ok
test_06_closing_customer_list (__main__.TestBasicScenario) ... ok

----------------------------------------------------------------------
Ran 6 tests in 23.367s

OK
"""