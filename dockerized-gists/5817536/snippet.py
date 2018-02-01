from selenium.webdriver import ActionChains

class Select2(object):
    def __init__(self, element):
        self.browser = element.parent
        self.replaced_element = element
        self.element = browser.find_element_by_id(
            's2id_{0}'.format(element.get_attribute('id')))

    def click(self):
        click_element = ActionChains(self.browser)\
            .click_and_hold(self.element)\
            .release(self.element)
        click_element.perform()

    def open(self):
        if not self.is_open:
            self.click()

    def close(self):
        if self.is_open:
            self.click()

    @property
    def is_open(self):
        return element_has_class(self.element, 'select2-dropdown-open')

    @property
    def dropdown(self):
        return browser.find_element_by_id('select2-drop')

    @property
    def items(self):
        self.open()
        item_divs = self.dropdown.find_elements_by_css_selector(
            'ul.select2-results li div.select2-result-label')
        return [div.text for div in item_divs]