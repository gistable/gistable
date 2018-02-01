'''
YouTube History Scraping Script by Yuval Adam

Requires Selenium and PhantomJS

A major FUCK YOU to Youtube/Google for not having a proper API for this
<^>(-_-)<^>
'''

from selenium import webdriver
from time import sleep

driver = webdriver.PhantomJS()
driver.get('http://youtube.com/feed/history')
driver.find_element_by_css_selector('div#yt-masthead-signin button').click()

driver.find_element_by_css_selector('form#gaia_loginform input#Email').send_keys('your_username_here')
driver.find_element_by_css_selector('form#gaia_loginform input#Passwd').send_keys('your_password_here')
driver.find_element_by_css_selector('form#gaia_loginform input#signIn').click()

videos = []

try:
    while True:
        driver.find_element_by_css_selector('button.feed-load-more').click()
        videos = driver.find_elements_by_class_name('yt-lockup-tile')
        print 'Accumulated {} videos'.format(len(videos))
        sleep(2)
except:
    # expect to fail on ElementNotVisibleException
    # this happens once no more videos can be loaded
    pass

with open('youtube_history.txt', 'w') as f:
    for video in videos:
        id, title = [video.get_attribute(x) for x in [
            'data-context-item-id', 'data-context-item-title']]
        title = title.encode('utf8', 'ignore')
        f.write('http://youtube.com/watch?v={}    {}\\n'.format(id, title))
