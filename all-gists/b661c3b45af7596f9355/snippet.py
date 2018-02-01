from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

class WaitBrowser(object):
    
    def __init__(self, **kw):
        self.browser  = webdriver.PhantomJS()
    

   def readystate_complete(self):
       # AFAICT Selenium offers no better way to wait for the document to be loaded,
       # if one is in ignorance of its contents.
       return self.browser.execute_script("return document.readyState") == "complete"

    def wait(self, timeout=30):
        WebDriverWait(self.browser, timeout).until(self.readystate_complete)
    

wb = WaitBrowser()
wb.browser.get('http://example.com')
wb.wait()

    