from scrapy.spider import BaseSpider
 
class MindhacksSpider(BaseSpider):
    domain_name = "mindhacks.cn"
    start_urls = ["http://mindhacks.cn/"]
 
    def parse(self, response):
        return []
 
SPIDER = MindhacksSpider()
#######################################################
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from myproject.items import MyItem

class MySpider(BaseSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = [
        'http://www.example.com/1.html',
        'http://www.example.com/2.html',
        'http://www.example.com/3.html',
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for h3 in hxs.select('//h3').extract():
            yield MyItem(title=h3)

        for url in hxs.select('//a/@href').extract():
            yield Request(url, callback=self.parse)
            
############################################################
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item

class MySpider(CrawlSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(SgmlLinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(SgmlLinkExtractor(allow=('item\.php', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.log('Hi, this is an item page! %s' % response.url)

        hxs = HtmlXPathSelector(response)
        item = Item()
        item['id'] = hxs.select('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = hxs.select('//td[@id="item_name"]/text()').extract()
        item['description'] = hxs.select('//td[@id="item_description"]/text()').extract()
        return item
        
        
################################################################################################
from scrapy import log
from scrapy.contrib.spiders import XMLFeedSpider
from myproject.items import TestItem

class MySpider(XMLFeedSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com/feed.xml']
    iterator = 'iternodes' # This is actually unnecesary, since it's the default value
    itertag = 'item'

    def parse_node(self, response, node):
        log.msg('Hi, this is a <%s> node!: %s' % (self.itertag, ''.join(node.extract())))

        item = Item()
        item['id'] = node.select('@id').extract()
        item['name'] = node.select('name').extract()
        item['description'] = node.select('description').extract()
        return item
        
#########################################################################
from scrapy import log
from scrapy.contrib.spiders import CSVFeedSpider
from myproject.items import TestItem

class MySpider(CSVFeedSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com/feed.csv']
    delimiter = ';'
    headers = ['id', 'name', 'description']

    def parse_row(self, response, row):
        log.msg('Hi, this is a row!: %r' % row)

        item = TestItem()
        item['id'] = row['id']
        item['name'] = row['name']
        item['description'] = row['description']
        return item
        
##########################################################################



def parse(self, response):
    items = []
    hxs = HtmlXPathSelector(response)
    posts = hxs.x('//h1/a/@href').extract()
    items.extend([self.make_requests_from_url(url).replace(callback=self.parse_post)
                  for url in posts])
 
    page_links = hxs.x('//div[@class="wp-pagenavi"]/a[not(@title)]')
    for link in page_links:
        if link.x('text()').extract()[0] == u'\xbb':
            url = link.x('@href').extract()[0]
            items.append(self.make_requests_from_url(url))
 
    return items
    
################################################################################

def parse_post(self, response):
    item = BlogCrawlItem()
    item.url = unicode(response.url)
    item.raw = response.body_as_unicode()
    return [item]
################################################################################
class BlogCrawlItem(ScrapedItem):
    def __init__(self):
        ScrapedItem.__init__(self)
        self.url = ''
 
    def __str__(self):
        return 'BlogCrawlItem(url: %s)' % self.url
################################################################################
