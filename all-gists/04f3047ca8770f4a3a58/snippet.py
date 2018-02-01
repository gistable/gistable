import subprocess
import unittest

from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, task

from my_project.spiders.spider1 import Spider1
from my_project.spiders.spider2 import Spider2


fixture_server = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', '4012'])

def setup_crawler(spider_class, **kwargs):
    splitter = ';'
    urls = kwargs['urls'].split(splitter)
    kwargs['urls'] = splitter.join(['http://127.0.0.1:4012/my_project/test/fixtures/' + url for url in urls])
    spider = spider_class(**kwargs)

    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    return spider

spider1 = setup_crawler(
  spider_class=Spider1,
  site_id=654321,
  urls='spider1/mini.csv',
)

spider2 = setup_crawler(
  spider_class=Spider2,
  site_id=654321,
  urls='spider2/mini.xml',
)

task.deferLater(reactor, 1, reactor.stop)
reactor.run()
fixture_server.kill()


class SpidersTests(unittest.TestCase):
  def test_spider1(self):
    self.assertEqual(len(spider1.results_sent[0]), 4)

  def test_xml_getter(self):
    self.assertEqual(len(spider2.results_sent[0]), 2)
