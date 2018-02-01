from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
desired_capabilities['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
                                                                  'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                                                  'Chrome/39.0.2171.95 Safari/537.36'
driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
