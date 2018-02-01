from selenium import webdriver
from selenium.webdriver.common.by import By

class Page(object):
    """
    Base class that all page models can inherit from
    """

    def __init__(self, selenium_driver, base_url='https://test.axial.net', parent=None):
        self.base_url = base_url
        self.driver = selenium_driver
        self.timeout = 30
        self.parent = parent
        self.tabs = {}

    def _open(self, url):
        url = self.base_url + url
        self.driver.get(url)
        assert self.on_page(), 'Did not land on %s' % url

    def find_element(self, *loc):
        return self.driver.find_element(*loc)

    def open(self):
        self._open(self.url)

    def on_page(self):
        return self.driver.current_url == (self.base_url + self.url)

    def script(self, src):
        return self.driver.execute_script(src)

    def send_keys(self, loc, value, clear_first=True, click_first=True):
        try:
            loc = getattr(self, '_%s' % loc)
            if click_first:
                self.find_element(*loc).click()
            if clear_first:
                self.find_element(*loc).clear()
            self.find_element(*loc).send_keys(value)
        except AttributeError:
            print '%s page does not have "%s" locator' % (self, loc)


class LoginPage(Page):
    """
    Model the login page.
    """
    url = '/login/'

    # Locators
    _email_loc = (By.ID, 'id_email')
    _password_loc = (By.ID, 'id_password')
    _submit_loc = (By.CSS_SELECTOR, '#sign_in_bttn')

    # Actions
    def open(self):
        self._open(self.url)

    def type_email(self, email):
        self.find_element(*self._email_loc).send_keys(email)

    def type_password(self, password):
        self.find_element(*self._password_loc).send_keys(password)

    def submit(self):
        self.find_element(*self._submit_loc).click()


def test_that_user_can_login(driver, username, password):
    """
    Test that the user identified by the given credentials can login
    """
    login_page = LoginPage(driver)

    login_page.open()
    login_page.type_email(username)
    login_page.type_password(password)
    login_page.submit()

    # Make sure we got past the login page
    assert not login_page.on_page(), "Couldn't get past the login page"


def main():
    try:
        # Selenium 
        driver = webdriver.Firefox()
        username = 'scuba.steve@axial.net'
        password = 'wouldntyouliketoknow'
        test_that_user_can_login(driver, username, password)
    finally:
        # Close the browser window
        driver.close()

if __name__ == '__main__':
    main()
