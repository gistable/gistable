#!/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from random import randint
from selenium import webdriver
from pyvirtualdisplay import Display

class MuncherySpider():
	def __init__(self):
		self.url_to_crawl = "https://munchery.com/"
		self.all_items = []

	# Open headless chromedriver
	def start_driver(self):
		print('starting driver...')
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		self.driver = webdriver.Chrome("/var/chromedriver/chromedriver")
		sleep(4)

	# Close chromedriver
	def close_driver(self):
		print('closing driver...')
		self.display.stop()
		self.driver.quit()
		print('closed!')

	# Tell the browser to get a page
	def get_page(self, url):
		print('getting page...')
		self.driver.get(url)
		sleep(randint(2,3))

	# Munchery front gate page
	def login(self):
		print('getting pass the gate page...')
		try:
			form = self.driver.find_element_by_xpath('//*[@class="signup-login-form"]')
			form.find_element_by_xpath('.//*[@class="user-input email"]').send_keys('iam@alexhoang.net')
			form.find_element_by_xpath('.//*[@class="user-input zip-code"]').send_keys('94011')
			form.find_element_by_xpath('.//*[@class="large orange button"]').click()
			sleep(randint(3,5))
		except Exception:
			pass

	def grab_list_items(self):
		print('grabbing list of items...')
		for div in self.driver.find_elements_by_xpath('//ul[@class="menu-items row"]//li'):
			data = self.process_elements(div)
			if data:
				self.all_items.append(data)
			else:
				pass

	def process_elements(self, div):
		prd_image = ''
		prd_title = ''
		prd_price = ''

		try:
			prd_image = div.find_element_by_xpath('.//*[@class="photo item-photo"]').get_attribute("source")
			prd_title = div.find_element_by_xpath('.//*[@class="text ng-binding"]').text
			prd_price = div.find_element_by_xpath('.//*[@class="price ng-scope ng-binding"]').text
		except Exception:
			pass

		if prd_image and prd_title and prd_price:
			single_item_info = {
				'image': prd_image.encode('UTF-8'),
				'title': prd_title.encode('UTF-8'),
				'price': prd_price.encode('UTF-8')
			}
			return single_item_info
		else:
			return False

	def parse(self):
		self.start_driver()
		self.get_page(self.url_to_crawl)
		self.login()
		self.grab_list_items()
		self.close_driver()

		if self.all_items:
			return self.all_items
		else:
			return False, False

		
# Run spider
Munchery = MuncherySpider()
items_list = Munchery.parse()

# Do something with the data touched
for item in items_list:
	print(item)
