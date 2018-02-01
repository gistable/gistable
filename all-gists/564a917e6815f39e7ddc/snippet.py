""" This script bulk downloads emoji from a slack channel """
import os, time, urllib
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

display = Display(visible=0, size=(800, 600))
display.start()

driver = webdriver.Chrome("DRIVER LOCATION")
driver.get("https://yourslackteam.slack.com/customize/emoji")
login_input = driver.find_element_by_name("email")
login_input.send_keys("youremail@email.com")
pwd_input = driver.find_element_by_name("password")
time.sleep(1)
pwd_input.send_keys("yourpassword")
pwd_input.send_keys(Keys.RETURN)

emojispans = driver.find_elements_by_class_name("emoji-wrapper")
if not os.path.exists("slack_emoji"):
	os.makedirs("slack_emoji")

for emoji in emojispans:
	emoji_url = emoji.get_attribute("data-original")
	split_emoji = emoji_url.split("/")
	emoji_name = split_emoji[4]
	print emoji_name
	urllib.urlretrieve(emoji_url, "slack_emoji/"+emoji_name)
	driver.close()
display.stop()