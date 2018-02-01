"""
Hooking up Selenium to Behave.

For details, see:
http://pyuseful.wordpress.com/2012/11/08/running-cucumber-style-tests-in-django-using-behave/

"""
import logging

from selenium import webdriver


def before_all(context):
    selenium_logger = logging.getLogger(
        'selenium.webdriver.remote.remote_connection')
    selenium_logger.setLevel(logging.WARN)

    context.driver = webdriver.Firefox()
    context.driver.implicitly_wait(3)


def after_all(context):
    context.driver.quit()