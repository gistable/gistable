# A downloader middleware automatically to redirect pages containing a rel=canonical in their contents to the canonical url (if the page itself is not the canonical one),

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.url import url_is_from_spider
from scrapy.http import HtmlResponse
from scrapy import log

class RelCanonicalMiddleware(object):
    _extractor = SgmlLinkExtractor(restrict_xpaths=['//head/link[@rel="canonical"]'], tags=['link'], attrs=['href'])

    def process_response(self, request, response, spider):
        if isinstance(response, HtmlResponse) and response.body and getattr(spider, 'follow_canonical_links', False):
            rel_canonical = self._extractor.extract_links(response)
            if rel_canonical:
                rel_canonical = rel_canonical[0].url
                if rel_canonical != request.url and url_is_from_spider(rel_canonical, spider):
                    log.msg("Redirecting (rel=\"canonical\") to %s from %s" % (rel_canonical, request), level=log.DEBUG, spider=spider)
                    return request.replace(url=rel_canonical, callback=lambda r: r if r.status == 200 else response)
        return response

# Snippet imported from snippets.scrapy.org (which no longer works)
# author: pablo
# date  : Aug 27, 2010
