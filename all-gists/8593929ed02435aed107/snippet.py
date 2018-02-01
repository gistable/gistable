# -*- coding: utf-8 -*-
import sys
import time
# include your version of selenium webdriver in archive
sys.path.insert(0, 'selenium-2.18.zip')

import logging
from selenium import *
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

__author__="dirzhov"
__date__ ="$Jan 26, 2012 5:30:55 PM$"

class WebDriverBackedSelenium(object):

#    def __init__(self, host, port, browserStartCommand, browserURL=None):
#        self.driver = WebDriver(command_executor='http://'+str(host)+':'+str(port)+'/wd/hub',
#               desired_capabilities={"browserName":browserStartCommand})
    def __init__(self, driver):
        self.driver = driver

    def setExtensionJs(self, extensionJs):
        pass
    
    def stop(self):
        self.driver.quit()
        
    def start(self, browserConfigurationOptions=None):
        pass
    
    def click(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        el.click()

    def double_click(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.double_click(el).perform()
    
    def context_menu(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.context_click(el).perform()
    
    def click_at(self,locator,coordString):
        pass
    
    def double_click_at(self,locator,coordString):
        pass
    
    def context_menu_at(self,locator,coordString):
        pass
    
    def fire_event(self,locator,eventName):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        if (eventName=='keydown'):
            el.send_keys(Keys.DOWN)
        elif (eventName=='blur'):
            el.send_keys(Keys.TAB)
    
    def focus(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        el.send_keys("")
    
    def key_press(self,locator,keySequence):
        pass
    
    def shift_key_down(self):
        pass
    
    def shift_key_up(self):
        pass
    
    def meta_key_down(self):
        pass
    
    def meta_key_up(self):
        pass
    
    def alt_key_down(self):
        pass
    
    def alt_key_up(self):
        pass
    
    def control_key_down(self):
        pass
    
    def control_key_up(self):
        pass
    
    def key_down(self,locator,keySequence):
        """Sends a key press only, without releasing it.
        Should only be used with modifier keys (Control, Alt and Shift).

        :Args:
         - key: The modifier key to send. Values are defined in Keys class.
         - target: The element to send keys.
           If None, sends a key to current focused element.
        """
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.key_down(keySequence,el).perform()
    
    def key_up(self,locator,keySequence):
        """
        Releases a modifier key.

        :Args:
         - key: The modifier key to send. Values are defined in Keys class.
         - target: The element to send keys.
           If None, sends a key to current focused element.
        """
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.key_up(keySequence,el).perform()
    
    def mouse_over(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.mouse_move(el).perform()
    
    def mouse_out(self,locator):
        pass
    
    def mouse_down(self,locator):
        pass
    
    def mouse_down_right(self,locator):
        pass
    
    def mouse_down_at(self,locator,coordString):
        pass
    
    def mouse_down_right_at(self,locator,coordString):
        pass
    
    def mouse_up(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.release(el).perform()
    
    def mouse_up_right(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.release(el).perform()

    def mouse_up_at(self,locator,coordString):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.release(el).perform()
    
    def mouse_up_right_at(self,locator,coordString):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.release(el).perform()
    
    def mouse_move(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(el).perform()
    
    def mouse_move_at(self,locator,coordString):
        offset = coordString.split[","]
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element_with_offset(el,offset[0],offset[2]).perform()
    
    def type(self,locator,value):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        if value == "":
            el.clear()
        else:
            el.send_keys(value)
    
    def type_keys(self,locator,value):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        el.send_keys(value)
    
    def set_speed(self,value):
        pass
    
    def get_speed(self):
        pass
    
    def get_log(self):
        pass
    
    def check(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        el.click()
    
    def uncheck(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        el.click()
    
    def select(self,selectLocator,optionLocator):
        el = self.driver.find_element(self.getBy(selectLocator), self.getValue(selectLocator))
        select = Select(el)
        logging.debug(select.options)
        if ("label=" in optionLocator):
            select.select_by_visible_text(optionLocator[6:])
        elif ("value=" in optionLocator):
            select.select_by_value(optionLocator[6:])
            
    
    def add_selection(self,locator,optionLocator):
        pass
    
    def remove_selection(self,locator,optionLocator):
        el = self.driver.find_element(self.getBy(selectLocator), self.getValue(selectLocator))
        select = Select(el)
        logging.debug(select.options)
        if ("label=" in optionLocator):
            select.deselect_by_visible_text(optionLocator[6:])
        elif ("value=" in optionLocator):
            select.deselect_by_value(optionLocator[6:])
    
    def remove_all_selections(self,locator):
        el = self.driver.find_element(self.getBy(selectLocator), self.getValue(selectLocator))
        select = Select(el)
        select.deselect_all()
    
    def submit(self,formLocator):
        el = self.driver.find_element(self.getBy(formLocator), self.getValue(formLocator))
        el.submit()
    
    def open(self,url,ignoreResponseCode=True):
        self.driver.get(url)
    
    def open_window(self,url,windowID):
        pass
    
    def select_window(self,windowID):
        #el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        self.driver.switch_to_window(windowID)
    
    def select_pop_up(self,windowID):
        pass
    
    def deselect_pop_up(self):
        pass
    
    def select_frame(self,locator):
        if (locator == "relative=up" or locator == "relative=top"):
            self.driver.switch_to_default_content()
        else:
            el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
            self.driver.switch_to_frame(el)
    
    def get_whether_this_frame_match_frame_expression(self,currentFrameString,target):
        pass
    
    def get_whether_this_window_match_window_expression(self,currentWindowString,target):
        pass
    
    def wait_for_pop_up(self,windowID,timeout):
        # temporarily
        time.sleep(5)
    
    def choose_cancel_on_next_confirmation(self):
        pass
    
    def choose_ok_on_next_confirmation(self):
        pass
    
    def answer_on_next_prompt(self,answer):
        pass
    
    def go_back(self):
        self.driver.back()
    
    def refresh(self):
        self.driver.refresh()
    
    def close(self):
        self.driver.close()
    
    def is_alert_present(self):
        pass
    
    def is_prompt_present(self):
        pass
    
    def is_confirmation_present(self):
        pass
    
    def get_alert(self):
        pass
    
    def get_confirmation(self):
        pass
    
    def get_prompt(self):
        pass
    
    def get_location(self):
        return self.driver.current_url
    
    def get_title(self):
        return self.driver.title
    
    def get_body_text(self):
        return self.driver.page_source
    
    def get_value(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.get_attribute('value')
    
    def get_text(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.text
    
    def highlight(self,locator):
        pass
    
    def get_eval(self,script):
        return self.driver.execute_script(script)
    
    def is_checked(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.get_attribute("checked")
    
    def get_table(self,tableCellAddress):
        pass
    
    def get_selected_labels(self,selectLocator):
        pass
    
    def get_selected_label(self,selectLocator):
        pass
    
    def get_selected_values(self,selectLocator):
        pass
    
    def get_selected_value(self,selectLocator):
        pass
    
    def get_selected_indexes(self,selectLocator):
        pass
    
    def get_selected_index(self,selectLocator):
        pass
    
    def get_selected_ids(self,selectLocator):
        pass
    
    def get_selected_id(self,selectLocator):
        pass
    
    def is_something_selected(self,selectLocator):
        pass
    
    def get_select_options(self,selectLocator):
        pass
    
    def get_attribute(self,attributeLocator):
        s = attributeLocator.rpartition("@")
        locator = s[0] 
        attribute = s[2]
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.get_attribute(attribute)
    
    def is_text_present(self,pattern):
        try: 
            el = self.driver.find_element_by_xpath("//*[contains(text(),'%s')]" % pattern)
            return True
        except NoSuchElementException, e: 
            return False
    
    def is_element_present(self,locator):
        try:
            el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
            el.is_displayed()
            return True
        except Exception as e:
            return False
    
    def is_visible(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.is_displayed()
    
    def is_editable(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.is_enabled()
    
    def get_all_buttons(self):
        pass
    
    def get_all_links(self):
        pass
    
    def get_all_fields(self):
        pass
    
    def get_attribute_from_all_windows(self,attributeName):
        pass
    
    def dragdrop(self,locator,movementsString):
        self.drag_and_drop(locator,movementsString)
    
    def set_mouse_speed(self,pixels):
        pass
    
    def get_mouse_speed(self):
        pass
    
    def drag_and_drop(self,locator,movementsString):
        offset = movementsString.split(',')
        fromEl = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        actionChains = ActionChains(self.driver)
        actionChains.drag_and_drop_by_offset(fromEl, offset[0], offset[2]).perform()
    
    def drag_and_drop_to_object(self,locatorOfObjectToBeDragged,locatorOfDragDestinationObject):
        fromEl = self.driver.find_element(self.getBy(locatorOfObjectToBeDragged), self.getValue(locatorOfObjectToBeDragged))
        toEl = self.driver.find_element(self.getBy(locatorOfDragDestinationObject), self.getValue(locatorOfDragDestinationObject))
        actionChains = ActionChains(self.driver)
        actionChains.drag_and_drop(fromEl, toEl).perform()
    
    def window_focus(self):
        self.driver.switch_to_default_content()
    
    def window_maximize(self):
        self.driver.execute_script("if (window.screen){window.moveTo(0, 0);window.resizeTo(window.screen.availWidth,window.screen.availHeight);};")
    
    def get_all_window_ids(self):
        return self.driver.window_handles
    
    def get_all_window_names(self):
        win_names = []
        for i in self.driver.window_handles:
            self.select_window(i)
            name = self.driver.title
            win_names.append(name)
        return win_names 
    
    def get_all_window_titles(self):
        pass
    
    def get_html_source(self):
        return self.driver.page_source
    
    def set_cursor_position(self,locator,position):
        pass
    
    def get_element_index(self,locator):
        pass
    
    def is_ordered(self,locator1,locator2):
        pass
    
    def get_element_position_left(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.location["left"]
    
    def get_element_position_top(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.location["top"]
    
    def get_element_width(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.size["width"]
    
    def get_element_height(self,locator):
        el = self.driver.find_element(self.getBy(locator), self.getValue(locator))
        return el.size["height"]
    
    def get_cursor_position(self,locator):
        pass
    
    def get_expression(self,expression):
        pass
    
    def get_xpath_count(self,xpath):
        els = self.driver.find_elements(self.getBy(xpath), self.getValue(xpath))
        return len(els)
    
    def get_css_count(self,css):
        els = self.driver.find_elements(self.getBy(css), self.getValue(css))
        return len(els) 
    
    def assign_id(self,locator,identifier):
        pass
    
    def allow_native_xpath(self,allow):
        pass
    
    def ignore_attributes_without_value(self,ignore):
        pass
    
    def wait_for_condition(self,script,timeout):
        pass
    
    def set_timeout(self,timeout):
        pass
    
    def wait_for_page_to_load(self,timeout):
        pass
    
    def wait_for_frame_to_load(self,frameAddress,timeout):
        pass
    
    def get_cookie(self):
        return self.driver.get_cookies()
    
    def get_cookie_by_name(self,name):
        return self.driver.get_cookie(name)
    
    def is_cookie_present(self,name):
        pass
    
    def create_cookie(self,nameValuePair,optionsString):
        pass
    
    def delete_cookie(self,name,optionsString):
        self.driver.delete_cookie(name)
    
    def delete_all_visible_cookies(self):
        pass
    
    def set_browser_log_level(self,logLevel):
        pass
    
    def run_script(self,script,args=[]):
        self.driver.execute_script(script, *args)
    
    def add_location_strategy(self,strategyName,functionDefinition):
        pass
    
    def capture_entire_page_screenshot(self,filename,kwargs):
        pass
    
    def rollup(self,rollupName,kwargs):
        pass
    
    def add_script(self,scriptContent,scriptTagId):
        pass
    
    def remove_script(self,scriptTagId):
        pass
    
    def use_xpath_library(self,libraryName):
        pass
    
    def set_context(self,context):
        pass
    
    def attach_file(self,fieldLocator,fileLocator):
        pass
    
    def capture_screenshot(self,filename):
        pass
    
    def capture_screenshot_to_string(self):
        return self.driver.get_screenshot_as_base64()
    
    def captureNetworkTraffic(self, type):
        pass
    
    def capture_network_traffic(self, type):
        pass
    
    def addCustomRequestHeader(self, key, value):
        pass
    
    def add_custom_request_header(self, key, value):
        pass
    
    def capture_entire_page_screenshot_to_string(self,kwargs):
        pass
    
    def shut_down_selenium_server(self):
        pass
    
    def retrieve_last_remote_control_logs(self):
        pass
    
    def key_down_native(self,keycode):
        pass
    
    def key_up_native(self,keycode):
        pass
    
    def key_press_native(self,keycode):
        pass
    

    def getBy(self, locator):
        by = locator[:locator.find("=")]
        if (by == "xpath"):
            return By.XPATH
        elif (by == "id"):
            return By.ID
        elif (by == "css"):
            return By.CSS_SELECTOR
        elif (by == "name"):
            return By.NAME
        elif (by == "link"):
            return By.LINK_TEXT
        else:
            return By.ID
    def getValue(self, locator):
        return locator[locator.find("=")+1:]

if __name__ == '__main__':
    driver = WebDriver(command_executor='http://localhost:4444/wd/hub',
           desired_capabilities={"browserName":"internet explorer"})
    wbd = WebDriverBackedSelenium(driver)
    wbd.stop()