from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class HackernewsSpider(BaseSpider):
  name = 'hackernews'
  allowed_domains = []
  start_urls = ['http://news.ycombinator.com']
  def parse(self, response):
    if 'news.ycombinator.com' in response.url:
        hxs = HtmlXPathSelector(response)
        titles = sites = hxs.select('//td[@class="title"]//a/text()')
        for title in titles:
            print title.extract()
