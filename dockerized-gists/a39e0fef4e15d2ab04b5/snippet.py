from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()
driver.get('http://google.com')

# Log in to the developer console.
driver.find_element_by_id('Email').send_keys(args.google_email)
driver.find_element_by_id('Passwd').send_keys(args.google_password)
driver.find_element_by_id('Passwd').send_keys(Keys.RETURN)

# Create the initial project.
elem = WebDriverWait(driver, 45).until(
    EC.presence_of_element_located((By.ID, 'projects-create'))
)
elem.click()