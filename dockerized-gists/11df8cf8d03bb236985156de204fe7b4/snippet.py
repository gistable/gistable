# This work with selenium

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from splinter.driver.webdriver import BaseWebDriver, WebDriverElement

options = Options()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

browser = BaseWebDriver()
browser.driver = Chrome(chrome_options=options)

browser.visit('http://example.com')


# With splinter there is 2 options :
# Splinter API only

from splinter import Browser
from splinter.driver.webdriver.chrome import Options

options = Options()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

browser = Browser('chrome', options=options)

browser.visit('http://example.com')


# Splinter and selenium API

from splinter import Browser
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

browser = Browser('chrome', options=options)

browser.visit('http://example.com')