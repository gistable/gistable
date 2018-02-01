#! /usr/bin/env python

import unittest
from selenium import webdriver

class TestGmail(unittest.TestCase):

	def setUp(self):
		self.driver = webdriver.Firefox()

	def testLogin(self):
		driver = self.driver
		driver.get('http://www.gmail.com')
		self.assertIn('Gmail', driver.title)
		loginBox = driver.find_element_by_id('Email')
		loginBox.send_keys('email.address@gmail.com')
		pwBox = driver.find_element_by_id('Passwd')
		pwBox.send_keys('!SuperSecretpassw0rd')
		signinBtn = driver.find_element_by_id('signIn')
		signinBtn.click()

	def tearDown(self):
		self.driver.quit()

if __name__ == '__main__':
	unittest.main(verbosity=2)