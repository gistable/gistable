# Import unittest module for creating unit tests
import unittest

# Import time module to implement 
import time

# Import the Selenium 2 module (aka "webdriver")
from selenium import webdriver

# For automating data input
from selenium.webdriver.common.keys import Keys

# For providing custom configurations for Chrome to run
from selenium.webdriver.chrome.options import Options

# --------------------------------------
# Provide a class for the unit test case
class PythonOrgSearchChrome(unittest.TestCase):

	# Anything declared in setUp will be executed for all test cases
	def setUp(self):
		# Define a variable to hold all the configurations we want
		chrome_options = webdriver.ChromeOptions()

		# Define chrome option configurations here ...

		# Create driver, pass it the path to the chromedriver file and the special configurations you want to run
		self.driver = webdriver.Chrome(executable_path='/Library/Python/2.7/site-packages/selenium/webdriver/chrome/chromedriver', chrome_options=chrome_options)
		
		# Window management hacks because I'm using OS X. On Windows or Linux you could just specify these as a ChromeOption
		self.driver.set_window_size(1920, 1080)
		self.driver.maximize_window()
	
	# An individual test case. Must start with 'test_' (as per unittest module)
	def test_search_in_python_chrome(self):
		# Assigning a local variable for the global driver
		driver = self.driver

		# Go to google.com
		driver.get('http://www.google.com')
		
		# A test to ensure the page has keyword Google in the page title
		self.assertIn("Google", driver.title)

		# Pauses the screen for 5 seconds so we have time to confirm it arrived at the right page
		time.sleep(5) 

		# Find and select the search box element on the page
		search_box = driver.find_element_by_name('q')

		# Enter text into the search box
		search_box.send_keys('Devin Mancuso')

		# Make sure the results page returned something
		assert "No results found." not in driver.page_source

		# Submit the search box form
		search_box.submit() 

		# Can also use Keys function to submit
		#search_box.send_keys(Keys.RETURN)

		# Another pause so we can see what's going on
		time.sleep(5)

		# Take a screenshot of the results
		driver.save_screenshot('screenshot-deskto-chrome.png')

	# Anything declared in tearDown will be executed for all test cases
	def tearDown(self):
		# Close the browser. 
		# Note close() will close the current tab, if its the last tab it will close the browser. To close the browser entirely use quit()
		self.driver.close()

class PythonOrgSearchFireFox(unittest.TestCase):

	def setUp(self):
		# Define the FireFox driver this time so we use Firefox to run the test
		self.driver = webdriver.Firefox()
		
		# Window management hacks because I'm using OS X. On Windows or Linux you could just specify these as webdriver options
		self.driver.set_window_size(1920, 1080)
		self.driver.maximize_window()
		
	def test_search_in_python_firefox(self):
		# Assigning a local variable for the global driver
		driver = self.driver

		# Go to google.com
		driver.get('http://www.google.com')
		
		# A test to ensure the page has keyword Google in the page title
		self.assertIn("Google", driver.title)

		# Pauses the screen for 5 seconds so we have time to confirm it arrived at the right page
		time.sleep(5) 

		# Find and select the search box element on the page
		search_box = driver.find_element_by_name('q')

		# Enter text into the search box
		search_box.send_keys('Devin Mancuso')

		# Make sure the results page returned something
		assert "No results found." not in driver.page_source

		# Submit the search box form
		search_box.submit() 

		# Can also use Keys function to submit
		#search_box.send_keys(Keys.RETURN)

		# Another pause so we can see what's going on
		time.sleep(5)

		# Take a screenshot of the results
		driver.save_screenshot('screenshot-deskto-firefox.png')

	# Anything declared in tearDown will be executed for all test cases
	def tearDown(self):
		# Close the browser. 
		# Note close() will close the current tab, if its the last tab it will close the browser. To close the browser entirely use quit()
		self.driver.close()

# Boilerplate code to start the unit tests
if __name__ == "__main__":
	unittest.main()		