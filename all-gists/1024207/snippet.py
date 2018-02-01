from scrapy import log
from scrapy.item import Item
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider


def NextURL():
    """
    Generate a list of URLs to crawl. You can query a database or come up with some other means
    Note that if you generate URLs to crawl from a scraped URL then you're better of using a 
    LinkExtractor instead: http://doc.scrapy.org/topics/link-extractors.html
    """
    list_of_urls = <make some database call here to return a URL to crawl>
    
    for next_url in list_of_urls:
        yield next_url



class YourScrapingSpider(XMLFeedSpider):
    """
    http://doc.scrapy.org/topics/spiders.html#xmlfeedspider
    """
    name = "MyScrapingSpider"
    
    ## an empty list means all domains are allowed (logic offloaded to business code)
    allowed_domains = []
    
    ## setup the generator that spits our next URLs to crawl. It is important to reuse this generator
    ## otherwise you'll always be returning the same URL
    url = NextURL()
    
    start_urls = []
    
    def start_requests(self):
        """
        NOTE: This method is ONLY CALLED ONCE by Scrapy (to kick things off).
        Get the first url to crawl and return a Request object
        This will be parsed to self.parse which will continue
        the process of parsing all the other generated URLs
        """

        ## grab the first URL to being crawling
        start_url = self.url.next()
        
        log.msg('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)
        
        ### important to yield, not return (not sure why return doesn't work here)
        yield request
    ##start_requests()

    
    def parse(self, response, node):
        """
        Parse the current response object, and return any Item and/or Request objects
        """
        log.msg("SCRAPING '%s'" % response.url)

        ## extract your data and yield as an Item (or DjangoItem if you're using django-celery)
        scraped_item = Item()
        scraped_item['some_value'] = "important value"
        yield scraped_item

        ## get the next URL to crawl
        next_url = self.url.next()
        yield Request(next_url)
    ##parse()