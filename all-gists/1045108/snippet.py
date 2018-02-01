from selenium import selenium
from scrapy.spider import BaseSpider
from scrapy.http import Request
import time
import lxml.html

class SeleniumSprider(BaseSpider):
    name = "selenium"
    allowed_domains = ['selenium.com']
    start_urls = ["http://localhost"]
    
    def __init__(self,  **kwargs):
        print kwargs
        self.sel = selenium("localhost", 4444, "*firefox","http://selenium.com/")
        self.sel.start()
    
    def parse(self, response):
        sel = self.sel
        sel.open("/index.aspx")
        sel.click("id=radioButton1")
        sel.select("genderOpt", "value=male")
        sel.type("nameTxt", "irfani")
        sel.click("link=Submit")
        time.sleep(1) #wait a second for page to load
        root = lxml.html.fromstring(sel.get_html_source())