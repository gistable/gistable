# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def create_browser():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.image', 2)
    profile.update_preferences()
    return webdriver.Firefox(profile)

driver = create_browser()
wait = ui.WebDriverWait(driver, 10)
driver.get("https://www.facebook.com")
driver.find_element_by_id('email').clear()
driver.find_element_by_id('email').send_keys('foo@bar.com')
driver.find_element_by_id('pass').clear()
driver.find_element_by_id('pass').send_keys('foobar')
driver.find_element_by_id('u_0_b').click()

try:
    wait.until(lambda driver: driver.find_element_by_id("pageNav"))
    profile_href = driver.find_element_by_id("pageNav").find_element_by_tag_name("a").get_attribute('href')
    driver.get(profile_href + "&sk=friends")
    contacts = driver.find_elements_by_xpath("//div[contains(@class, 'fsl')]/a")
    profile_urls = []
    for contact in contacts:
        profile_urls.append(contact.get_attribute('href'))
    for url in profile_urls:
        driver.get(url)
        driver.find_element_by_partial_link_text('Información').click()
        wait.until(lambda driver: driver.find_element_by_id("pagelet_basic"))
        date_of_birth = driver.find_element_by_id("pagelet_basic").find_element_by_tag_name("table").find_element_by_class_name("clearfix")
        username = driver.find_element_by_class_name("_8_2")
        print " %s date of birth is %s" % (username.text , date_of_birth.text)
except TimeoutException:
    print "Login, mal!"
driver.quit()
