import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select

locators = {
    "fisc": (By.CSS_SELECTOR, '[name="mytextarea"][multiple]')
}

class MultiSelect(Select):
    def __get__(self, obj, cls=None):
        s = Select(obj.driver.find_element(*self.locator))
        a = s.all_selected_options
        if len(a) == 0:
            return None
        return [x.text for x in a]

    def __getitem__(self, key):
        s = Select(self.driver.find_element(*self.locator))
        a = s.all_selected_options
        if len(a) == 0:
            return None
        selections = [x.text for x in a]
        return selections[key]

    def __delitem__(self, key):
        s = Select(self.driver.find_element(*self.locator))
        method = key[:key.find("=")]
        value = key[key.find("=") + 1:]
        if method == "value":
            s.deselect_by_value(value)
        elif method == "index":
            s.deselect_by_index(value)
        elif method == "text":
            s.deselect_by_visible_text(value)
        else:
            raise Exception("%s is an invalid locator" % item)

    def __len__(self):
        s = Select(self.driver.find_element(*self.locator))
        return len(s.all_selected_options)

    def append(self, item):
        s = Select(self.driver.find_element(*self.locator))
        method = item[:item.find("=")]
        value = item[item.find("=") + 1:]
        if method == "value":
            s.select_by_value(value)
        elif method == "index":
            s.select_by_index(value)
        elif method == "text":
            s.select_by_visible_text(value)
        else:
            raise Exception("%s is an invalid locator" % item)


class FISC(MultiSelect):
    def __init__(self):
        self.locator = locators["fisc"]


class TestWait(object):
    _timeout = 5
    
    fisc = FISC()
    
    def setup_method(self, method):
        self.driver = Firefox()
        self.driver.get("http://www.hscripts.com/tutorials/html/form-combobox.php")
        setattr(self.fisc, "driver", self.driver) 

    def teardown_method(self, method):
        self.driver.quit()

    @pytest.mark.get
    def test_get_one(self):
        self.fisc.append("value=three")
        assert(self.fisc[0] == "three")

    @pytest.mark.set
    def test_set(self):
        self.fisc.append("value=two")
        self.fisc.append("value=four")
        assert(len(self.fisc) == 2)
        assert(self.fisc[0] == "two")
        assert(self.fisc[1] == "four")
        
    @pytest.mark.delete
    def test_delete(self):
        self.fisc.append("value=two")
        self.fisc.append("value=four")
        del self.fisc["value=two"]
        assert(len(self.fisc) == 1)
        