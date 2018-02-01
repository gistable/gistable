from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from icone.items import Product 

class IconeSpider(CrawlSpider):

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk/designer-living/product-type/Lighting-Floor',
#        'http://www.icone.co.uk/designer-living/product-type/',
#        'http://www.icone.co.uk/designer-living/brand/',
#        'http://www.icone.co.uk/designer-living/designer/',
    ]
    rules = (Rule(SgmlLinkExtractor(allow=('/[0-9]+',)), callback='parse', follow=True), )

    def parse(self, response):
        log.msg('A response from %s just arrived!' % response.url)

        hxs = HtmlXPathSelector(response)
        products = hxs.select('//table/tr/td/table/tr[3]/td/table/tr/td/form/table/tr[2]/td/table')
        items = []
    
        for product in products:

          item = Product()
          item['name'] = product.select('./tr/td[@class="itemlist_design"]/strong/text()').extract()
          item['description'] = product.select('./tr/td[@class="itemlist_desc"]/text()').extract()
          item['price'] = product.select('./tr/td[@class="itemlist_price"]/a/span/strong/text()').extract() 
          item['image'] = product.select('./tr/td[@class="itemlist_img"]/a/img/@src').extract()

          items.append(item)

        return items
