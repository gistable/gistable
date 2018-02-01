#!/usr/bin/env python

"""Selenium WebDriver - Browser Benchmark

run 10 iterations of simple local test case with each driver:

Firefox (webdriver) vs. Chrome (chromedriver) vs. PhantomJS (ghostdriver).
"""

import unittest
from selenium import webdriver


class TestBrowser(unittest.TestCase):

    def get_page(self):
        self.driver.get('http://localhost:80/')
        body = self.driver.find_element_by_css_selector('body')
        self.assertIn('It works!', body.text)

    def tearDown(self):
        self.driver.quit()


class TestFirefox(TestBrowser):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_page(self):
        self.get_page()


class TestChrome(TestBrowser):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_page(self):
        self.get_page()
        

class TestPhantomJS(TestBrowser):
    def setUp(self):
        self.driver = webdriver.PhantomJS()

    def test_page(self):
        self.get_page()
        
        
if __name__ == '__main__':

    def run_tests(test_case_class, num_times):
        test = unittest.TestLoader().loadTestsFromTestCase(test_case_class)
        suite = unittest.TestSuite()
        suite.addTests([test for _ in range(num_times)])
        unittest.TextTestRunner().run(suite)

    num_times = 10

    print '\nrunning with Firefox...'
    run_tests(TestFirefox, num_times)

    print '\nrunning with Chrome...'
    run_tests(TestChrome, num_times)

    print '\nrunning with PhantomJS...'
    run_tests(TestPhantomJS, num_times)
