import csv, time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

applicant_name = # your name
applicant_email = # your email
applicant_address =  # your physical address
occupation = # your occupation

# names.csv file needs to be one column, "Last name, First name"

with open('names.csv', 'rb') as wh_csv:
    reader = csv.reader(wh_csv)
    for row in reader:
        name = row[0]
        driver = webdriver.Chrome()
        driver.get('https://forms.whitehouse.gov/webform/financial-disclosures?initialWidth=544&childId=forall-iframe-embed-1&parentTitle=Financial%20Disclosures%20%7C%20whitehouse.gov&parentUrl=https%3A%2F%2Fwww.whitehouse.gov%2Ffinancial-disclosures')
        my_name = driver.find_element_by_xpath('//input[@id=\'edit-submitted-applicants-name\']')
        my_name.send_keys(applicant_name)
        my_email = driver.find_element_by_xpath('//input[@id=\'edit-submitted-applicants-email-address\']')
        my_email.send_keys(applicant_email)
        my_address = driver.find_element_by_xpath('//input[@id=\'edit-submitted-applicants-address\']')
        my_address.send_keys(applicant_address)
        my_occupation = driver.find_element_by_xpath('//input[@id=\'edit-submitted-occupation\']')
        my_occupation.send_keys(occupation)
        my_occupation = driver.find_element_by_xpath('//input[@id=\'edit-submitted-individual-for-whom-you-would-like-to-request-a-copy-of-their-public-financial-disclosure-reports\']')
        my_occupation.send_keys(str(name))
        select = Select(driver.find_element_by_id('edit-submitted-please-indicate-the-calendar-year-for-which-you-are-requesting-public-financial-disclosure-reports'))
        select.select_by_visible_text('2017')
        driver.find_element_by_xpath('//input[@id=\'edit-submitted-please-check-here-to-agree-to-the-statement-below-1\']').click()
        driver.find_element_by_xpath('//input[@class=\'webform-submit button-primary btn form-submit\']').click()
        time.sleep(3)
        print "requested %s" % (name)
        driver.close()