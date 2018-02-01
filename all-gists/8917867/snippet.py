from scrapy.spider import  Spider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.item import Item, Field
import urllib

class Question(Item):
    tags = Field()
    answers = Field()
    votes = Field()
    date = Field()
    link = Field()

class ArgSpider(CrawlSpider):
    """
    
    Scrapes first 15 stackoverflow.com questions containing "query" within a given "tag" and 
    displays links, number of votes etc in the terminal. 

    Usage:
    
      ~: scrapy crawl StackSpider -a tag=[your tag] -a query=[your query]

    For example
        
       ~: scrapy crawl StackSpider -a tag=python -a query="crawling a website"


    """

    name = "StackSpider"

    def __init__(self,tag=None,query=None,*args,**kwargs):
        super(ArgSpider,self).__init__(*args,**kwargs)
        self.start_urls = []
        urlTemplate = "http://stackoverflow.com/search?q=%5B{tag}%5D{query}"
        query = urllib.quote(query)
        self.start_urls.append(urlTemplate.format(tag=tag,query=query))


    def parse(self,response):
        """

        @url http://stackoverflow.com/search?q=%5Bpython%5Dfiltering"
        @returns items 15
        @returns requests 0 1
        @scrapes votes answers date link

        """
        sel = Selector(response)
        elems = sel.css('.question-summary')
        results = []
        for elem in elems:
            item = Question()
            item["tags"] = elem.css('.post-tag::text').extract()
            item["votes"] = elem.css('.vote-count-post').xpath('.//strong/text()').extract()
            item["answers"] = elem.css('.status').xpath('.//strong/text()').extract()
            item["date"] = elem.css('.relativetime').xpath('.//@title').extract()
            link = elem.css('.result-link').xpath('.//a/@href').extract()
            item["link"] = link
            results.append(item)
        return results