import re

from scrapy.link import Link
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

class SoupLinkExtractor(object):
    def __init__(self, *args, **kwargs):
        super(SoupLinkExtractor, self).__init__()
        allow_re = kwargs.get('allow', None)
        self._allow = re.compile(allow_re) if allow_re else None
    
    def extract_links(self, response):
        raw_follow_urls = []
        
        soup = BeautifulSoup(response.body_as_unicode())

        anchors = soup.findAll('a')
        for anchor in anchors:
            anchor_href = anchor.get('href', None)
            if anchor_href and not anchor_href.startswith('#'):
                raw_follow_urls.append(anchor_href)
                
        potential_follow_urls = [urljoin(response.url, raw_follow_url) for raw_follow_url in raw_follow_urls]
        
        if self._allow:
            follow_urls = [potential_follow_url for potential_follow_url in potential_follow_urls if self._allow.search(potential_follow_url) is not None]
        else:
            follow_urls = potential_follow_urls
            
        return [Link(url = follow_url) for follow_url in follow_urls]
