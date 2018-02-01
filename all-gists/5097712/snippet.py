# -*- coding: utf-8 -*-

import pycurl
from BeautifulSoup import BeautifulSoup


class BruteFrocePinterestCrawler:
    def __init__(self):
        self.content = ''
        self.url = ''

    def read_page(self, buffer):
        self.content = self.content + buffer

    def show_page(self):
        print self.content

    def curl_page(self, url):
        self.url = url
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEFUNCTION, self.read_page)
        curl.perform()
        curl.close()

    def import_page(self, filename):
        self.url = filename
        self.content = open(filename).read()

    def get_image_urls(self):
        soup = BeautifulSoup(''.join(self.content))
        image_tags = soup.findAll('img', {"class": "PinImageImg"})
        for each in image_tags:
            print each['src']

if __name__ == "__main__":
    crawler = BruteFrocePinterestCrawler()
    crawler.curl_page('http://pinterest.com/rightson/bueno/')
    crawler.get_image_urls()
