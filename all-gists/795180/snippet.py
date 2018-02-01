from scrapy.spider import BaseSpider

# Requires this patch:
# https://github.com/joehillen/scrapy/commit/6301adcfe9933b91b3918a93387e669165a215c9
from scrapy.selector import PyQuerySelector

class DmozSpiderPyQuery(BaseSpider):
    name = "pyquery"
    allowed_domains = ["dmoz.org"]
    start_urls = [
       "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
       "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    def parse(self, response):
        pq = PyQuerySelector(response)
        sites = pq('ul li')
        for site in sites:
            title = pq(site).find('a').text()
            link = pq(site).find('a').attr.href
            desc = pq(site).text()
            print title, link, desc