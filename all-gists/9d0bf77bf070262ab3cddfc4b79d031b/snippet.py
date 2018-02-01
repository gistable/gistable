# coding: utf-8

import urllib.parse
import urllib.request

class Rakuten(object):

    response = None

    def __init__(self, applicationId=None, format="json"):
        self.params = {
            "applicationId": applicationId,
            "format": format
        }

    def request(self, url, **kwargs):
        self.params.update(kwargs)

        query_string = urllib.parse.urlencode(self.params)

        if query_string:
            url = "{}?{}".format(url, query_string)
        
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            self.response = f.read()
            self.url = f.geturl()
        return self

    @property
    def raw(self):
        return self.response

    @property
    def parse(self):
        return getattr(self, self.params["format"])(self.response.decode())
    
    def json(self, response):
        import json
        return json.loads(response)

    def xml(self, response):
        import xml.etree.ElementTree as ET
        return ET.fromstring(response)

class IchibaItem(Rakuten):
    
    def search(self, **kwargs):
        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20140222"
        return self.request(url, **kwargs)

    def ranking(self, **kwargs):
        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20120927"
        return self.request(url, **kwargs)

class IchibaGenre(Rakuten):

    def search(self, **kwargs):
        url = "https://app.rakuten.co.jp/services/api/IchibaGenre/Search/20140222"
        return self.request(url, **kwargs)

class IchibaTag(Rakuten):

    def search(self, **kwargs):
        url = "https://app.rakuten.co.jp/services/api/IchibaTag/Search/20140222"
        return self.request(url, **kwargs)

class Product(Rakuten):

    def search(self, **kwargs):
        url = "https://app.rakuten.co.jp/services/api/Product/Search/20140305"
        return self.request(url, **kwargs)

if __name__ == "__main__":

    item = IchibaItem(**{
        "applicationId": "applicationId",
        "format": "json"})

    response = item.search(**{"keyword": "楽天"})
    json = response.parse
    print(json)
