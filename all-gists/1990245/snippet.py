### Locating UI elements ###

# By ID
<div id="coolestWidgetEvah">...</div>
element = driver.find_element_by_id("coolestWidgetEvah")
or
from selenium.webdriver.common.by import By
element = driver.find_element(by=By.ID, value="coolestWidgetEvah")

# By class name:
<div class="cheese"><span>Cheddar</span></div><div class="cheese"><span>Gouda</span></div>
cheeses = driver.find_elements_by_class_name("cheese")
or
from selenium.webdriver.common.by import By
cheeses = driver.find_elements(By.CLASS_NAME, "cheese")

# By tag name:
<iframe src="..."></iframe>
frame = driver.find_element_by_tag_name("iframe")
or
from selenium.webdriver.common.by import By
frame = driver.find_element(By.TAG_NAME, "iframe")

# By name
<input name="cheese" type="text"/>
cheese = driver.find_element_by_name("cheese")
or
from selenium.webdriver.common.by import By
cheese = driver.find_element(By.NAME, "cheese")

# By link text
<a href="http://www.google.com/search?q=cheese">cheese</a>
cheese = driver.find_element_by_link_text("cheese")
or
from selenium.webdriver.common.by import By
cheese = driver.find_element(By.LINK_TEXT, "cheese")

# By partial link text
<a href="http://www.google.com/search?q=cheese">search for cheese</a>
cheese = driver.find_element_by_partial_link_text("cheese")
or
from selenium.webdriver.common.by import By
cheese = driver.find_element(By.PARTIAL_LINK_TEXT, "cheese")

# By CSS
<div id="food"><span class="dairy">milk</span><span class="dairy aged">cheese</span></div>
cheese = driver.find_element_by_css_selector("#food span.dairy.aged")
or
from selenium.webdriver.common.by import By
cheese = driver.find_element(By.CSS_SELECTOR, "#food span.dairy.aged")

# By XPATH
<input type="text" name="example" />
inputs = driver.find_elements_by_xpath("//input")
or
from selenium.webdriver.common.by import By
inputs = driver.find_elements(By.XPATH, "//input")



### Filling in forms ###

# This will deselect all OPTIONs from the first SELECT on the page
# and then select the OPTION with the displayed text of “Edam”.

from selenium.webdriver.support.ui import Select
select = Select(driver.find_element_by_tag_name("select"))
select.deselect_all()
select.select_by_visible_text("Edam")


### Moving between windows and frames

### Popup dialogs ###

### Navigation: history and location ###