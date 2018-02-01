mail_address = ''
password = ''

from selenium import webdriver

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'
PHANTOMJS_ARG = {'phantomjs.page.settings.userAgent': UA}
driver = webdriver.PhantomJS(desired_capabilities=PHANTOMJS_ARG)

url = 'https://www.google.com/accounts/Login?hl=ja&continue=http://www.google.co.jp/'
driver.get(url)

driver.find_element_by_id("Email").send_keys(mail_address)
driver.find_element_by_id("next").click()
driver.find_element_by_id("Passwd").send_keys(password)
driver.find_element_by_id("signIn").click()