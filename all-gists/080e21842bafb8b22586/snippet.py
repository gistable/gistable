#!/usr/bin/env python

# * Note: phantomjs must be in your PATH
#
# This script:
# - Navigates to www.google.com
# - Intentionally raises an exception by searching for a nonexistent element
# - Leaves behind a screenshot in exception.png

import unittest
from selenium import webdriver
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support.events import AbstractEventListener

class ScreenshotListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        screenshot_name = "exception.png"
        driver.get_screenshot_as_file(screenshot_name)
        print("Screenshot saved as '%s'" % screenshot_name)

class TestDemo(unittest.TestCase):
    def test_demo(self):

        pjsdriver = webdriver.PhantomJS("phantomjs")
        d = EventFiringWebDriver(pjsdriver, ScreenshotListener())

        d.get("http://www.google.com")
        d.find_element_by_css_selector("div.that-does-not-exist")

if __name__ == '__main__':
        unittest.main()
