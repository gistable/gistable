from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest as ut
import time

class NewPaymentTest(ut.TestCase):

	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_can_sign_up(self):
		self.browser.get('http://localhost:8000')

		# He clicks the "Subscribe" button
		stripe_button = self.browser.find_element_by_css_selector('button.stripe-button-el')
		stripe_button.click()

		# Test that Stripe has taken over the screen
		## We switch context to the stripe iframe with name stripe_checkout_app
		self.browser.switch_to.frame('stripe_checkout_app')
		stripe_overlay = self.browser.find_element_by_css_selector('.overlayView')
		classes = stripe_overlay.get_attribute('class')
		self.assertEqual(classes, 'overlayView active')

		# Proceed through the Stripe workflow and redirect to a confirmation page
		email_input = self.browser.find_element_by_css_selector('#email')
		email_input.send_keys('hello@example.com')
		email_input.send_keys(Keys.TAB)
  
    # the time.sleep statements are here to let selenium catch up with stripe
		card_input = self.browser.find_element_by_css_selector('#card_number')
		card_input.send_keys('4242')
		time.sleep(0.25)
		card_input.send_keys('4242')
		time.sleep(0.25)
		card_input.send_keys('4242')
		time.sleep(0.25)
		card_input.send_keys('4242')
		time.sleep(0.25)

		exp_input = self.browser.find_element_by_css_selector('#cc-exp')
		exp_input.send_keys('08')
		time.sleep(0.25)
		exp_input.send_keys('16')

		csc_input = self.browser.find_element_by_css_selector('#cc-csc')
		csc_input.send_keys('424')

		submit_button = self.browser.find_element_by_css_selector('#submitButton')
		submit_button.click()

		## The part where he's redirected, time.sleep is here to allow the redirect to catch up
		self.browser.switch_to_default_content()
		time.sleep(4)
		
		# The thank you 
		self.assertIn('Thank you!', self.browser.page_source)

if __name__ == '__main__':
	ut.main()