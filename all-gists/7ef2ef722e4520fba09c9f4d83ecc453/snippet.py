# coding: utf-8

import urllib.parse
import urllib.request

import xml.etree.ElementTree as ET


class Yahoo(object):

    response = None

    def __init__(self, appid=None):
        self.params = {
            "appid": appid
        }

    # APIを叩く
    def request(self, url, **kwargs):
        self.params.update(kwargs)

        query_string = urllib.parse.urlencode(self.params)

        if query_string:
            url = url + query_string

        with urllib.request.urlopen(url) as f:
            self.response = f.read()
            self.request_url = f.geturl()
        return self

    # 生のレスポンスデータ
    @property
    def raw(self):
        return self.response

    # XMLをパースしたデータ
    @property
    def parse(self):
        if self.response is None:
            raise
        return ET.fromstring(self.response)

    @property
    def total(self):
        return self.parse.attrib["totalResultsAvailable"]

    @property
    def hits(self):
        return int(self.parse.attrib["totalResultsReturned"])

    @property
    def first(self):
        return int(self.parse.attrib["firstResultPosition"])
    
    @property
    def page(self):
        return self.first + self.hits - 1


class Shopping(Yahoo):

    NS = {
        "itemSearch": "urn:yahoo:jp:itemSearch",
        "itemLookup": "urn:yahoo:jp:itemLookup"
    }

    def lookup(self, **kwargs):
        self.prefix = "itemLookup"
        url = "http://shopping.yahooapis.jp/ShoppingWebService/V1/itemLookup?"
        return self.request(url, **kwargs)

    def search(self, **kwargs):
        self.prefix = "itemSearch"
        url = "http://shopping.yahooapis.jp/ShoppingWebService/V1/itemSearch?"
        return self.request(url, **kwargs)

    # 商品情報を取得するジェネレータ
    @property
    def items(self):
        match = "{}:Hit".format(self.prefix)
        for item in self.parse[0].findall(match, self.NS):
            self._item = item
            yield self

    def find(self, tag):
        item = self._item
        for t in tag.split("."):
            item = item.find("{}:{}".format(self.prefix, t), self.NS)
        return item

    @property
    def id(self):
        return self.find("Code").text

    @property
    def category(self):
        return self.find("Category.Current.Name").text

    @property
    def name(self):
        return self.find("Name").text

    @property
    def url(self):
        return self.find("Url").text

    @property
    def price(self):
        return self.find("Price").text

    @property
    def fixedprice(self):
        return self.find("PriceLabel.FixedPrice").text

    @property
    def shopname(self):
        return self.find("Store.Name").text

    @property
    def jancode(self):
        return self.find("JanCode").text


if __name__ == "__main__":
    # APPIDを取得して下さい。
    APPID = "APPID"

    shopping = Shopping(APPID)
    response = shopping.search(**{"query": "Python"})
    for item in response.items:
        print(item.find("Name").text)
        print(item.find("Image.Medium").text)
