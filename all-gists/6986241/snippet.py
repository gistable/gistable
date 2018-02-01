from scrapy.selector import HtmlXPathSelector 
from scrapy.spider import BaseSpider 
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor 
from scrapy.utils.url import urljoin_rfc 
from scrapy.http import Request 

class MySpider(BaseSpider): 
    name = ’test’ 
    allowed_domains = [’xxxx.com’] 
    start_urls = [ 
        ’http://www.xxxx.com’, 
    ] 
    download_delay = 10 
    def parse(self, response): 
        for link in SgmlLinkExtractor(allow=" product.htm\?id=\d+").extract_links(response): 
            yield Request(link.url,callback=self.parse_detail) 
        hxs = HtmlXPathSelector(response) 
        for url in hxs.select(’//a/@href’).extract(): 
            url =  self._urljoin(response,url) 
            #print url 
            yield Request(url, callback=self.parse) 

    def parse_detail(self, response): 
        hxs = HtmlXPathSelector(response) 
        what_u_want= hxs.select("/xpath/text()").extract()[0] 
        print ’url=’,response.url, what_u_want.strip() 
        return 

    def _urljoin(self, response, url): 
        """Helper to convert relative urls to absolute""" 
        return urljoin_rfc(response.url, url, response.encoding)