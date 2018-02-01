"""
Tweeting by controlling Firefox via Python + selenium
http://selenium-python.readthedocs.org/

This script:

- Opens up Firefox
- Goes to https://www.twitter.com
- Clicks the login button
- logs you in (assuming you have your twitter password in a file named `mypassword.txt`...)
- Fills out the Tweet box with some text
- Takes a screenshot of twitter.com as it currently appears in your browser
- Attaches the screenshot to the Tweet
- Sends the tweet

Obviously you should be using tweepy + the Twitter API if you actually
want to programmatically work with Twitter data and be efficient about it
But it's fun watching Python control the browser interactively...
"""

from selenium import webdriver
MY_SCREEN_NAME = 'yourtwitternamegoeshere'
# don't be an idiot by hardcoding your password in the actual script
MY_PASSWORD = open("mypassword.txt").read().strip()


driver = webdriver.Firefox()
driver.get("https://www.twitter.com")

## Login
el = driver.find_element_by_css_selector('button.Button.js-login')
el.click()
# fill out the username
el = driver.find_element_by_css_selector("input.email-input")
# "type" in your screen name
el.send_keys(MY_SCREEN_NAME)
# fill out your password...again, another reason to use the API (with OAuth) and NOT
# your browser. At the very least, don't hardcode your password into the script

# "type" in your password
driver.find_element_by_css_selector(".LoginForm-password > input").send_keys(MY_PASSWORD)
# Submit the form
el.submit()

## Now write the tweet
# Select the tweet box
el = driver.find_element_by_id('tweet-box-home-timeline')
# ...you might have to do this twice if it doesn't respond right away
el.send_keys("""whoa I just tweeted from Firefox, using Python and Selenium
https://gist.github.com/dannguyen/8a6fa49253c1d6a0eb92""")

# let's take a screenshot just to prove it
driver.save_screenshot("i-am-on-twitter.png")
# crop and show only top 400 pixels because selenium will screenshot the ENTIRE page
from PIL import Image
img = Image.open("i-am-on-twitter.png")
# absolute filepath is needed
cropped_filename = "/tmp/cropped-i-am-on-twitter.png"
img.crop((0, 0, img.size[0], 400)).save(cropped_filename)
# Upload the image
driver.find_element_by_css_selector('input.file-input').send_keys(cropped_filename)

# wait till image is uploaded until going forward
# http://selenium-python.readthedocs.org/waits.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
try:
    print("...uploading", cropped_filename)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.js-show-preview'))
    )
except:
    print("Unexpected error:", sys.exc_info()[0])
else:
    # it was a successful upload...
    # Now send the tweet by clicking the button
    driver.find_element_by_css_selector('button.tweet-action').click()
