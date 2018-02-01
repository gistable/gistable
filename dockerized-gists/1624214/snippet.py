from selenium.common.exceptions import NoSuchElementException, TimeoutException


class DomHelper(object):
    driver = None
    waiter = None

    def open_page(self, url):
        self.driver.get(url)

    def reload_page(self):
        self.driver.refresh()

    def print_el(self, element):
        print 'tag: ' + element.tag_name + ' id: ' + element.get_attribute('id') + ' class: ' + element.get_attribute('class') + ' text: ' + element.text

    def get_el(self, selector):
        if isinstance(selector, (str, unicode)):
            return self.driver.find_element_by_css_selector(selector)
        else:
            return selector

    def get_els(self, selector):
        if isinstance(selector, (str, unicode)):
            return self.driver.find_elements_by_css_selector(selector)
        else:
            return selector

    def get_child_el(self, parent, selector):
        try:
            return parent.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return None
    
    def get_child_els(self, parent, selector):
        return parent.find_elements_by_css_selector(selector)
           
    def is_el_present(self, selector):
        try:
            self.driver.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException:
            return False

    def verify_el_present(self, selector):
        if not self.is_el_present(selector):
            raise Exception('Element %s not found' % selector)
            
    def is_el_visible(self, selector):
        return self.get_el(selector).is_displayed()
        
    def click_button(self, selector):
        if self.driver.name == 'iPhone':
            self.driver.execute_script('$("%s").trigger("tap")' % (selector))
        else:
            self.get_el(selector).click()

    def enter_text_field(self, selector, text):
        text_field = self.get_el(selector)
        text_field.clear()
        text_field.send_keys(text)

    def select_checkbox(self, selector, name, deselect=False):
        found_checkbox = False
        checkboxes = self.get_els(selector)
        for checkbox in checkboxes:
            if checkbox.get_attribute('name') == name:
                found_checkbox = True
                if not deselect and not checkbox.is_selected():
                    checkbox.click()
                if deselect and checkbox.is_selected():
                    checkbox.click()
        if not found_checkbox:
            raise Exception('Checkbox %s not found.' % (name))

    def select_option(self, selector, value):
        found_option = False
        options = self.get_els(selector)
        for option in options:
            if option.get_attribute('value') == str(value):
                found_option = True
                option.click()
        if not found_option:
            raise Exception('Option %s not found' % (value))

    def get_selected_option(self, selector):
        options = self.get_els(selector)
        for option in options:
            if option.is_selected():
                return option.get_attribute('value')

    def is_option_selected(self, selector, value):
        options = self.get_els(selector)
        for option in options:
            if option.is_selected() != (value == option.get_attribute('value')):
                print option.get_attribute('value')
                return False
        return True

    def is_text_equal(self, selector, text):
        return self.get_el(selector).text == text

    def verify_inputs_checked(self, selector, checked):
        checkboxes = self.get_els(selector)
        for checkbox in checkboxes:
            name = checkbox.get_attribute('name')
            if checkbox.is_selected() != (name in checked):
                raise Exception('Input isnt checked as expected - %s' % (name))

    def verify_option_selected(self, selector, value):
        if not self.is_option_selected(selector, value):
            raise Exception('Option isnt selected as expected')
    
    def verify_radio_value(self, selector, value):
        value = str(value)
        radios = self.get_els(selector)
        for radio in radios:
            radio_value = radio.get_attribute('value')
            if radio.is_selected() and radio_value != value:
                raise Exception('Radio with value %s is checked and shouldnt be' % radio_value)
            elif not radio.is_selected() and radio_value == value:
                raise Exception('Radio with value %s isnt checked and should be' % radio_value)
                
    def verify_text_field(self, selector, text):
        text_field = self.get_el(selector)
        value = text_field.get_attribute('value')
        if value != text:
            raise Exception('Text field contains %s, not %s' % (value, text))
    
    def verify_text_value(self, selector, value):
        text_field = self.get_el(selector)
        if text_field.get_attribute('value') != value:
            raise Exception('Value of %s not equal to "%s" - instead saw "%s"' % (selector, value, text_field.get_attribute('value')))

    def verify_text_of_el(self, selector, text):
        if not self.is_text_equal(selector, text):
            raise Exception('Text of %s not equal to "%s" - instead saw "%s"' % (selector, text, self.get_el(selector).text))

    def verify_text_in_els(self, selector, text):
        els = self.get_els(selector)
        found_text = False
        for el in els:
            if text in el.text:
                found_text = True
        if not found_text:
            raise Exception('Didnt find text: %s' % (text))
    
    def verify_text_not_in_els(self, selector, text):
        els = self.get_els(selector)
        found_text = False
        for el in els:
            if text in el.text:
                found_text = True
        if found_text:
            raise Exception('Found text: %s' % (text))
    
    def is_button_enabled(self, selector):
        return (self.get_el(selector).get_attribute('disabled') == 'false')

    def check_title(self, title):
        return self.driver.title == title or self.driver.title == 'eatdifferent.com: ' + title

    def wait_for(self, condition):
        self.waiter.until(lambda driver: condition())

    def check_num(self, selector, num):
        els = self.get_els(selector)
        return len(els) == num

    def wait_for_num_els(self, selector, num):
        try:
            self.waiter.until(lambda driver: self.check_num(selector, num))
        except TimeoutException:
            raise Exception('Never saw %s number of els for %s' % (num, selector))

    def wait_for_visible(self, selector):
        try:
            self.waiter.until(lambda driver: self.is_el_visible(selector))
        except TimeoutException:
            raise Exception('Never saw element %s become visible' % (selector))

    def wait_for_hidden(self, selector):
        try:
            self.waiter.until(lambda driver: not self.is_el_visible(selector))
        except TimeoutException:
            raise Exception('Never saw element %s become hidden' % (selector))
                 
    def wait_for_button(self, selector):
        try:
            self.waiter.until(lambda driver: self.is_button_enabled(selector))
        except TimeoutException:
            raise Exception('Never saw button %s enabled' % (selector))

    def wait_for_text(self, selector, text):
        try:
            self.waiter.until(lambda driver: self.is_text_equal(selector, text))
        except TimeoutException:
            raise Exception('Never saw text %s for %s' % (text, selector))

    def wait_for_el(self, selector):
        try:
            self.waiter.until(lambda driver: self.is_el_present(selector))
        except TimeoutException:
            raise Exception('Never saw element %s' % (selector))
    
    def wait_for_title(self, title):
        try:
            self.waiter.until(lambda driver: self.check_title(title))
        except TimeoutException:
            raise Exception('Never saw title change to %s' % (title))

    def __init__(self, driver, waiter):
        self.driver = driver
        self.waiter = waiter
