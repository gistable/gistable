from selenium import webdriver
import os
import subprocess


def before_all(context):
    get_browser(context)
    get_sut_url(context)

def after_all(context):
    context.browser.quit()

def get_browser(context):
    remote_url = os.getenv("REMOTE_URL", "")
    if remote_url == "":
        print "*** Running tests on PhantomJS ***"
        context.browser = webdriver.PhantomJS()
    else:
        print "*** Running tests on remote %s***"%remote_url
        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        desired_capabilities['platform'] = 'WINDOWS'
        context.browser = webdriver.Remote(
            desired_capabilities=desired_capabilities,
            command_executor = remote_url 
            )

def get_sut_url(context):
    context.sut_url = os.getenv("SUT_URL", "http://google.com")