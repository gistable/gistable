from scrapy.spider import BaseSpider
from scrapy.conf import settings
from scrapy.http import Request
from random import choice


class DoubleIPSpider(BaseSpider):
    name = "double_ip_test"
    allowed_domains = ["httpbin.org"]

    def start_requests(self):
        yield self.make_requests_from_url("http://httpbin.org/ip")
        yield self.make_requests_from_url("http://httpbin.org/ip")
        yield self.make_requests_from_url("http://httpbin.org/ip")
        yield self.make_requests_from_url("http://httpbin.org/ip")
        yield self.make_requests_from_url("http://httpbin.org/ip")

    def make_requests_from_url(self, url):
        if settings.get("BIND_TO_IP"):
            ip = choice(settings["BIND_TO_IP"])
            print(ip)
            return Request(url, dont_filter=True,
                           meta={'bindaddress': (
                                 ip,
                                 0)})
        else:
            return super(DoubleIPSpider, self).make_requests_from_url(url)

    def parse(self, response):
       print(response.body)
