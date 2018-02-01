''' 
Taking Screenshots with Appium

I'll be using Python and a sample iOS application from Apple's Developer Library
This tutorial assumes you understand how to run, launch, and interact with your application.

'''

from appium import webdriver
import os

desired_capabilities = {}

# Build and run the GLPaint app, then specify the absolute path below
# GLPaint can be downloaded from: https://developer.apple.com/library/ios/samplecode/GLPaint/Introduction/Intro.html
desired_capabilities['app'] = '/Users/jessicasachs/projects/demo-automation/demo-apps/compiled/GLPaint.app'
desired_capabilities['deviceName'] = 'iPhone Simulator'
desired_capabilities['platformName'] = 'iOS'
desired_capabilities['platformVersion'] = '7.1'

driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_capabilities)

directory = '%s/' % os.getcwd()
file_name = 'screenshot.png'

driver.save_screenshot(directory + file_name)