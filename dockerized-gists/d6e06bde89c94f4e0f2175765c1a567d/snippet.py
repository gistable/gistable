#!/usr/bin/env python

import datetime
import re
import smtplib
import time

from selenium import webdriver

PASSPORT_NUMBER = 'ADD PASSPORT NUMBER'
RESCHEDULE_URL = 'ADD URL FROM CONSULATE CONFIRMATION'
YOUR_EMAIL_ADDRESS = 'ADD YOUR EMAIL ADDRESS'

PHANTOMJS_PATH ='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs'
SLEEP = 20

def _select_contenu_win(driver):
    driver.switch_to_default_content()
    driver.switch_to_frame(driver.find_element_by_id('BODY_WIN'))
    driver.switch_to_frame(driver.find_element_by_id('CONTENU_WIN'))

def main():
    driver = webdriver.PhantomJS(PHANTOMJS_PATH)
    driver.get(RESCHEDULE_URL)

    time.sleep(SLEEP)

    _select_contenu_win(driver)
    driver.find_element_by_name('numeroPass').send_keys(PASSPORT_NUMBER)
    driver.find_element_by_id('bouton_valider_link').click()

    time.sleep(SLEEP)

    # Dismiss confirm
    _select_contenu_win(driver)
    driver.execute_script("%s" % 'window.confirm = function(message) { return true; }')
    driver.find_element_by_id('boutonChanger_link').click()

    time.sleep(SLEEP)

    _select_contenu_win(driver)
    text = driver.find_element_by_css_selector('#compTableau_Entete td:nth-child(2)').text
    driver.close()

    match = re.match(r'.*(?P<jour>[0-9]{2})\/(?P<mois>[0-9]{2})\/(?P<annee>[0-9]{4}).*', text)
    date = "%s/%s/%s" % (match.group('jour'), match.group('mois'), match.group('annee'))

    # Define your match criteria and method of contact (default to email)
    if int(match.group('mois')) == 5 and int(match.group('jour')) > 15:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('alan.consulate.news@gmail.com', 'assurance')
        server.sendmail(
            'alan.conuslate.news@gmail.com',
            YOUR_EMAIL_ADDRESS,
            '%s %s' % (date, PASSPORT_NUMBER),
        )
        server.quit()

    # Print incase you want you log to a file.
    print '%s: %s' % (datetime.datetime.now().isoformat(), date)


if __name__ == '__main__':
    main()