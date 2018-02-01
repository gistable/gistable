from selenium import webdriver
from selenium.webdriver.common.keys import Keys

usr = ""
pwd = ""

driver = webdriver.Firefox()
# or you can use Chrome(executable_path="/usr/bin/chromedriver")
driver.get("http://www.facebook.org")
assert "Facebook" in driver.title
elem = driver.find_element_by_id("email")
elem.send_keys(usr)
elem = driver.find_element_by_id("pass")
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)

elem = driver.find_element_by_css_selector(".input.textInput")
elem.send_keys("Posted using Python's Selenium WebDriver bindings!")
elem = driver.find_element_by_css_selector("input[value=\"Publicar\"]")
elem.click()



driver.close()