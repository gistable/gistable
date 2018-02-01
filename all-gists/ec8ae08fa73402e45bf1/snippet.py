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
		# Select which device you want to emulate by uncommenting it
		# More information at: https://sites.google.com/a/chromium.org/chromedriver/mobile-emulation
		mobile_emulation = { 
			#"deviceName": "Apple iPhone 3GS"
			#"deviceName": "Apple iPhone 4"
			#"deviceName": "Apple iPhone 5"
			#"deviceName": "Apple iPhone 6"
			#"deviceName": "Apple iPhone 6 Plus"
			#"deviceName": "BlackBerry Z10"
			#"deviceName": "BlackBerry Z30"
			#"deviceName": "Google Nexus 4"
			"deviceName": "Google Nexus 5"
			#"deviceName": "Google Nexus S"
			#"deviceName": "HTC Evo, Touch HD, Desire HD, Desire"
			#"deviceName": "HTC One X, EVO LTE"
			#"deviceName": "HTC Sensation, Evo 3D"
			#"deviceName": "LG Optimus 2X, Optimus 3D, Optimus Black"
			#"deviceName": "LG Optimus G"
			#"deviceName": "LG Optimus LTE, Optimus 4X HD" 
			#"deviceName": "LG Optimus One"
			#"deviceName": "Motorola Defy, Droid, Droid X, Milestone"
			#"deviceName": "Motorola Droid 3, Droid 4, Droid Razr, Atrix 4G, Atrix 2"
			#"deviceName": "Motorola Droid Razr HD"
			#"deviceName": "Nokia C5, C6, C7, N97, N8, X7"
			#"deviceName": "Nokia Lumia 7X0, Lumia 8XX, Lumia 900, N800, N810, N900"
			#"deviceName": "Samsung Galaxy Note 3"
			#"deviceName": "Samsung Galaxy Note II"
			#"deviceName": "Samsung Galaxy Note"
			#"deviceName": "Samsung Galaxy S III, Galaxy Nexus"
			#"deviceName": "Samsung Galaxy S, S II, W"
			#"deviceName": "Samsung Galaxy S4"
			#"deviceName": "Sony Xperia S, Ion"
			#"deviceName": "Sony Xperia Sola, U"
			#"deviceName": "Sony Xperia Z, Z1"
			#"deviceName": "Amazon Kindle Fire HDX 7″"
			#"deviceName": "Amazon Kindle Fire HDX 8.9″"
			#"deviceName": "Amazon Kindle Fire (First Generation)"
			#"deviceName": "Apple iPad 1 / 2 / iPad Mini"
			#"deviceName": "Apple iPad 3 / 4"
			#"deviceName": "BlackBerry PlayBook"
			#"deviceName": "Google Nexus 10"
			#"deviceName": "Google Nexus 7 2"
			#"deviceName": "Google Nexus 7"
			#"deviceName": "Motorola Xoom, Xyboard"
			#"deviceName": "Samsung Galaxy Tab 7.7, 8.9, 10.1"
			#"deviceName": "Samsung Galaxy Tab"
			#"deviceName": "Notebook with touch"
			
			# Or specify a specific build using the following two arguments
			#"deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
		    #"userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
		}
		
		# Define a variable to hold all the configurations we want
		chrome_options = webdriver.ChromeOptions()
		
		# Add the mobile emulation to the chrome options variable
		chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
		
		# Create driver, pass it the path to the chromedriver file and the special configurations you want to run
		self.driver = webdriver.Chrome(executable_path='/Library/Python/2.7/site-packages/selenium/webdriver/chrome/chromedriver', chrome_options=chrome_options)

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

# Boilerplate code to start the unit tests
if __name__ == "__main__":
	unittest.main()