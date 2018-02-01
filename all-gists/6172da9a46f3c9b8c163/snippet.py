from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, strftime

def waituntil(s):
    while strftime('%H:%M:%S') < s:
        print strftime('%H:%M:%S')
        sleep(1)

def login():
    driver.get('https://www.irctc.co.in/eticketing/loginHome.jsf')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.NAME, 'j_username'))
        ).send_keys(IRCTC_USERNAME)
    driver.find_element_by_name('j_password').send_keys(IRCTC_PASSWORD)
    driver.find_element_by_name('j_captcha').send_keys('')

def planjourney():
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'jpform:fromStation'))
        ).send_keys(FROM_STATION)
    driver.find_element_by_id('jpform:toStation').send_keys(TO_STATION)
    driver.find_element_by_id('jpform:journeyDateInputDate').send_keys(DATE)
    waituntil('09:59:50')
    driver.find_element_by_id('jpform:jpsubmit').click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.NAME, 'quota'))
        )[-1].click()
    driver.find_element_by_id('cllink-%s-%s-%s' % (TRAIN_NO, CLASS, CLASS_INDEX)).click()
    # WebDriverWait(driver, 60).until(
    #     EC.presence_of_all_elements_located((By.ID, '%s-%s-CK-0' % (TRAIN_NO, CLASS)))
    #     )[-1].click()

def filldetails():
    WebDriverWait(driver, 60).until(EC.title_contains('Book Ticket'))
    for name, el in zip(NAMES, driver.find_elements_by_class_name('psgn-name')):
        el.send_keys(name)
    for age, el in zip(AGES, driver.find_elements_by_class_name('psgn-age')):
        el.send_keys(age)
    for gender, el in zip(GENDERS, driver.find_elements_by_class_name('psgn-gender')):
        Select(el).select_by_value(gender)
    for berth, el in zip(BERTHS, driver.find_elements_by_class_name('psgn-berth-choice')):
        Select(el).select_by_value(berth)
    driver.find_element_by_id('addPassengerForm:autoUpgrade').click()
    driver.find_element_by_id('addPassengerForm:onlyConfirmBerths').click()

def sbi():
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.ID, 'PREFERRED'))
        )[-1].click()
    driver.find_element_by_id('validate').click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'username'))
        ).send_keys(SBI_USERNAME)
    driver.find_element_by_id('label2').send_keys(SBI_PASSWORD)
    driver.find_element_by_id('Button2').click()


IRCTC_USERNAME = 'IRCTC_USERNAME'
IRCTC_PASSWORD = 'IRCTC_PASSWORD'
FROM_STATION = 'VIJAYAWADA JN - BZA'
FROM_STATION_CODE = 'BZA'
TO_STATION = 'ASANSOL JN - ASN'
TO_STATION_CODE = 'ASN'
DATE = '02-01-2016'
TRAIN_NO = '12551'
CLASS = '3A'
CLASS_INDEX = '2'
NAMES = ['NAME 1', 'NAME 2', 'NAME 3']
AGES = ['18', '24', '32']
GENDERS = ['M', 'M', 'M']
BERTHS = ['LB', 'LB', 'MB']
SBI_USERNAME = 'SBI_USERNAME'
SBI_PASSWORD = 'SBI_PASSWORD'

if __name__ == '__main__':
    profile = webdriver.FirefoxProfile()
    profile.set_preference('webdriver.load.strategy', 'unstable')
    waituntil('09:59:00')
    driver = webdriver.Firefox(profile)
    login()
    planjourney()
    filldetails()
    sbi()
