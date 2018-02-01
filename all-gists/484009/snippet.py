#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Rolando Espinoza La fuente

from scrapy.conf import settings
from scrapy.core import signals
from scrapy.core.manager import scrapymanager
from scrapy.item import Item, Field
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher

from scrapy.contrib.loader import XPathItemLoader

def connect(signal):
    """Handy signal hook decorator"""
    def wrapper(func):
        dispatcher.connect(func, signal)
        return func
    return wrapper


class QuestionItem(Item):
    """Our SO Question Item"""
    title = Field()
    summary = Field()
    tags = Field()

    user = Field()
    posted = Field()

    votes = Field()
    answers = Field()
    views = Field()

class MySpider(BaseSpider):
    """Our ad-hoc spider"""
    name = "myspider"
    start_urls = ["http://stackoverflow.com/"]

    question_list_xpath = '//div[@id="content"]//div[contains(@class, "question-summary")]'

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for qxs in hxs.select(self.question_list_xpath):
            loader = XPathItemLoader(QuestionItem(), selector=qxs)
            loader.add_xpath('title', './/h3/a/text()')
            loader.add_xpath('summary', './/h3/a/@title')
            loader.add_xpath('tags', './/a[@rel="tag"]/text()')
            loader.add_xpath('user', './/div[@class="started"]/a[2]/text()')
            loader.add_xpath('posted', './/div[@class="started"]/a[1]/span/@title')
            loader.add_xpath('votes', './/div[@class="votes"]/div[1]/text()')
            loader.add_xpath('answers', './/div[contains(@class, "answered")]/div[1]/text()')
            loader.add_xpath('views', './/div[@class="views"]/div[1]/text()')

            yield loader.load_item()

def main():
    """Install item signal and run scrapy"""
    @connect(signals.item_passed)
    def catch_item(sender, item, **kwargs):
        print "Got:", item

    # shut off log
    settings.overrides['LOG_ENABLED'] = False

    scrapymanager.configure()

    spider = MySpider()
    scrapymanager.queue.append_spider(spider)

    print "STARTING ENGINE"
    scrapymanager.start()
    print "ENGINE STOPPED"

if __name__ == '__main__':
    main()