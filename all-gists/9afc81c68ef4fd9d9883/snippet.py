'''
Simple instagram photo downloader.
Requires python 2.7 and Selenium
make a folder in the working directory called pics for it to download the pictures into
usage:
instadl.py username password number_of_pagedowns
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import re
from selenium import *
import urllib
import os
from selenium.webdriver.common.keys import Keys
import sys
import math

if len(sys.argv) < 3 or "help" in sys.argv or "/?" in sys.argv or "--help" in sys.argv:
    print("Incorrect Usage, arguments follow:")
    print("username, password, number of page downs")
    print("example: instadl.py badtz thisisnotmypassword 1000")
    sys.exit()
browser = webdriver.Chrome('C:\\Windows\\chromedriver.exe')

browser.get("https://www.instagram.com/accounts/login/?force_classic_login") 
time.sleep(1)

print("Authenticating... \n")
browser.find_element_by_id("id_username").send_keys(sys.argv[1])
browser.find_element_by_id("id_password").send_keys(sys.argv[2])
browser.find_element_by_xpath("//*[@type='submit']").submit()

print("Loading images... \n")
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
browser.find_element_by_link_text('LOAD MORE').click()

percentamout = 100.00/float(sys.argv[3])
for i in range(1,int(sys.argv[3])):
    browser.find_element_by_tag_name('a').send_keys(Keys.PAGE_DOWN)
    currentpercent = float(i) * float(percentamout) + percentamout
    sys.stdout.write("\r%d%%" % currentpercent)
    sys.stdout.flush()
print("\n")

time.sleep(1)
output = browser.page_source.encode('utf-8')
f = open('output.html','w')
f.write(output)
f.close()
browser.quit()

pics = matching = [s for s in re.findall(r'"([^"]*)"', output) if "e35" in s and ".0.1.0.1.0." not in s and "\/\/" not in s]
print("Images Found: " + str(len(pics)) + "\n")
percentamout = 100.00/len(pics)
print("Downloading images... \n")
for i in range(0,len(pics)):
    if not os.path.isfile("pics/" + pics[i].split("_")[1] + ".png"):
        urllib.urlretrieve(pics[i], "pics/" + pics[i].split("_")[1] + ".png")
    currentpercent = float(i) * float(percentamout) + percentamout
    sys.stdout.write("\r%d%%" % currentpercent)
    sys.stdout.flush()
print("\n")
print("Complete!")