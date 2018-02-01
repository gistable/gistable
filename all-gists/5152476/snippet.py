# main.py:

from project.spiders.log_test import TestSpider as EstiloMASpider

from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import Crawler
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy import log, signals

def stop_reactor():
    reactor.stop()  # Stops reactor to prevent script from hanging

if __name__ == '__main__':
    dispatcher.connect(stop_reactor, signal=signals.engine_stopped)
    spider = EstiloMASpider()
    crawler = Crawler(get_project_settings())
    crawler.install()
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()

# log_test.py:

from scrapy import log
from scrapy.spider import BaseSpider

class TestSpider(BaseSpider):
    name = "logtest"
    start_urls = ["http://example.com/"]

    def parse(self, response):
        log.msg(response.url)
        log.msg('len: %s' % len(response.body))

# settings.py:

BOT_NAME = 'project'
SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'

# output:

stav@maia:/srv/stav/scrapie/crawler$ python main.py
2013-03-13 08:00:39-0600 [scrapy] INFO: http://www.iana.org/domains/example
2013-03-13 08:00:39-0600 [scrapy] INFO: len: 1111
2013-03-13 08:00:39-0600 [logtest] INFO: Closing spider (finished)
2013-03-13 08:00:39-0600 [logtest] INFO: Dumping Scrapy stats:
    {'downloader/request_bytes': 684,
     'downloader/request_count': 3,
     'downloader/request_method_count/GET': 3,
     'downloader/response_bytes': 1204,
     'downloader/response_count': 3,
     'downloader/response_status_count/200': 1,
     'downloader/response_status_count/302': 2,
     'finish_reason': 'finished',
     'finish_time': datetime.datetime(2013, 3, 13, 14, 0, 39, 867855),
     'response_received_count': 1,
     'scheduler/dequeued': 3,
     'scheduler/dequeued/memory': 3,
     'scheduler/enqueued': 3,
     'scheduler/enqueued/memory': 3,
     'start_time': datetime.datetime(2013, 3, 13, 14, 0, 39, 25226)}
2013-03-13 08:00:39-0600 [logtest] INFO: Spider closed (finished)

# structure:

"""
    stav@maia:/srv/stav/scrapie/crawler$ tree
    .
    ├── main.py
    ├── project
    │   ├── __init__.py
    │   ├── __init__.pyc
    │   ├── items.py
    │   ├── pipelines.py
    │   ├── settings.py
    │   ├── settings.pyc
    │   └── spiders
    │       ├── __init__.py
    │       ├── __init__.pyc
    │       ├── log_test.py
    │       └── log_test.pyc
    └── scrapy.cfg
"""

# environment

stav@maia:/srv/stav/scrapie/crawler$ scrapy version -v
Scrapy  : 0.17.0
lxml    : 2.3.2.0
libxml2 : 2.7.8
Twisted : 11.1.0
Python  : 2.7.3 (default, Aug  1 2012, 05:14:39) - [GCC 4.6.3]
Platform: Linux-3.2.0-38-generic-x86_64-with-Ubuntu-12.04-precise