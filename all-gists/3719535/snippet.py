from gcrawler import GCrawler, Downloader
import unittest
import urllib2
import logging
import traceback
from datetime import datetime
import re

logging.basicConfig(level=logging.DEBUG)

urls=['http://www.163.com', 'http://www.qq.com', 'http://www.sina.com.cn', 'http://www.sohu.com', 'http://www.yahoo.com', 'http://www.baidu.com', 'http://www.google.com', 'http://www.microsoft.com']

class DummySpider:
    def scheduler(self):
        for u in urls:
            yield u

    def worker(self, item):
        try:
            f = urllib2.urlopen(item)
            data = f.read()
            f.close()
            return (item, len(data))
        except:
            traceback.print_exc()
            return None

    def pipeline(self, results):
        for r in results:
            print "Downloaded : %s(%s)" % r

class DummyDownloader(Downloader):
    def pipeline(self, results):
        for r in results:
            r['datasize'] = len(r['data'])
            print "Data fetched : %(url)s(%(datasize)s)" % r

class ImagesDownloader(Downloader):
    def parse(self, result):
        pat_imgs = re.compile(u"<img.*src=\"([^\"]*)", re.I | re.U)
        imgs = list(set(pat_imgs.findall(result['data'])))
        print "Images count %s" % len(imgs)
        new_items = []
        for i in imgs:
            if i != "":
                item = dict(url=i, parse=None)
                new_items.append(item)
        return new_items, result

    def pipeline(self, results):
        print "== %s" % datetime.now()
        for r in results:
            r['datasize'] = len(r['data'])
            print "Image Data fetched : %(url)s(%(datasize)s)" % r

class TestGCrawler(unittest.TestCase):
    '''
    def testSpider(self):
        spider = DummySpider()
        crawler = GCrawler(spider, workers_count = 3)
        crawler.start()

    def testDownloader(self):
        spider = DummyDownloader(urls)
        crawler = GCrawler(spider, workers_count = 3)
        crawler.start()
    '''
    def testBatch(self):
        print "start at : %s" % datetime.now()
        spider = ImagesDownloader(['http://f1.163.com'])
        crawler = GCrawler(spider, workers_count = 3)
        crawler.start()

unittest.main()

