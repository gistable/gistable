from pyvirtualdisplay import Display
from selenium import webdriver
display = Display(visible=0, size=(800, 600))
display.start()
browser = webdriver.Chrome()
browser.get('http://www.google.com')
print browser.title
browser.quit()
display.stop()
