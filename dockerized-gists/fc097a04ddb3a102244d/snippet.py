"""
Standard and reliable module for starting up Selenium Webdriver, with custom user-agent and custom profiles.
"""

import os
import subprocess
import sys
import urllib

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def find_file(name, path):
    """Returns the path of a file in a directory"""

    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def find_selenium_server():
    """Returns the path of the 'standalone-server-standalone-x.x.x.jar' file."""

    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            try:
                if '-'.join(name.split('-')[:3]) == 'selenium-server-standalone':
                    return os.path.join(root, name)
            except IndexError:
                pass


def find_binary_file(name):
    """Returns the path of binary file in a given directory"""
    binary_path = None

    if sys.platform.startswith('win'):
        binary_path = find_file(name=name + '.exe', path=os.getcwd())
    elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        binary_path = find_file(name=name, path=os.getcwd())

    if binary_path:
        return binary_path
    else:
        print('{name} not found in the working directory.'.format(name=name))


def start_selenium_server():
    """Starts the Java Standalone Selenium Server."""

    seleniumserver_path = find_selenium_server()
    if not seleniumserver_path:
        print('The file "standalone-server-standalone-x.x.x.jar" not found.')
        return

    cmd = ['java', '-jar', seleniumserver_path]
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


def start_webdriver(driver_name, user_agent=None, profile_path=None):
    """Starts and returns a Selenium Webdriver.

    Args:
        driver_name (str): Name of the webdriver to be started [Chrome, Firefox, PhantomJs, HTMLUnit].
        user_agent (str): The user_agent string the webdriver should use.
        profile_path (str): The path of the browser profile [only for Firefox and Chrome].

    Returns:
        selenium.webdriver: A Selenium Webdriver according to the Args.
    """

    driver_name = driver_name.lower()
    driver = None

    if driver_name == 'htmlunit':
        while True:
            try:
                urllib.request.urlopen('http://localhost:4444/wd/hub/status')
            except urllib.error.URLError:
                start_selenium_server()
            else:
                break

        if user_agent:
            pass
        dcap = webdriver.DesiredCapabilities.HTMLUNITWITHJS
        driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
                                  desired_capabilities=dcap)

    if driver_name == 'firefox':
        if profile_path:
            fp = webdriver.FirefoxProfile(profile_path)
        else:
            fp = webdriver.FirefoxProfile()

        if user_agent:
            fp.set_preference('general.useragent.override', user_agent)

        driver = webdriver.Firefox(fp)

    if driver_name == 'chrome':
        opt = webdriver.chrome.options.Options()
        if user_agent:
            opt.add_argument('user-agent={user_agent}'.format(user_agent=user_agent))
        if profile_path:
            opt.add_argument('user-data-dir={profile_path}'.format(profile_path=profile_path))

        chromedriver_path = find_binary_file('chromedriver')
        driver = webdriver.Chrome(chromedriver_path, chrome_options=opt)

    if driver_name == 'phantomjs':
        dcap = DesiredCapabilities.PHANTOMJS
        if user_agent:
            dcap["phantomjs.page.settings.userAgent"] = user_agent

        phantomjs_path = find_binary_file('phantomjs')
        driver = webdriver.PhantomJS(phantomjs_path, desired_capabilities=dcap)

    return driver