#!/usr/local/bin/python3

#
# feedfinder.py
#
# Utils for finding feeds
#

import sys
from datetime import datetime
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

DEBUG = True

class Feed:
    url = None
    title = None
    feed_type = None
    is_main = False
    created = None

    def __init__(self, url, title=None, feed_type=None, is_main=False):
        self.url = url
        self.title = title
        self.feed_type = feed_type
        self.is_main = is_main
        self.created = datetime.utcnow()

    def __repr__(self):
        return '<%sFeed%s %s "%s">' % (
            ("%s-" % self.feed_type if not self.feed_type is None else ""),
            ('*' if self.is_main else ''), self.url, self.title)


class FeedFinder:
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'

    def _get_html(self, url):
        '''[Internal]
        Downloads the given URL with urllib2. Applies an custom User-agent
        to appear more like a browser and not a spider/crawler/bot.'''
        request = Request(url)
        request.add_header('User-Agent', self.USER_AGENT)
        
        response = urlopen(request)
        content = response.read()
        response.close()

        return content

    def _find_rss_feeds_in_header(self, soup):
        '''[Internal]
        Searches for RSS feed.
            <link type="application/rss+xml" rel="alternate" ...>
        Returns a list. Either empty if no feed URL was found or with Feed
        objects. Marks the shortest feed URL as the main one.
        Analogous to _find_atom_feeds_in_header().'''
        links = soup.find_all("link", attrs={'type': 'application/rss+xml', 'rel': 'alternate'})
        feeds = []
        for link in links:
            feeds.append(Feed(link["href"], link["title"], "RSS"))
        self._find_shortest_feed_url_and_update(feeds)
        return feeds
        
    def _find_atom_feeds_in_header(self, soup):
        '''[Internal]
        Searches for RSS feed.
            <link type="application/atom+xml" rel="alternate" ...>
        Returns a list. Either empty if no feed URL was found or with Feed
        objects. Marks the shortest feed URL as the main one.
        Analogous to _find_rss_feeds_in_header().'''
        links = soup.find_all("link", attrs={'type': 'application/atom+xml', 'rel': 'alternate'})
        feeds = []
        for link in links:
            feeds.append(Feed(link["href"], link["title"], "Atom"))
        self._find_shortest_feed_url_and_update(feeds)
        return feeds

    def _find_shortest_feed_url_and_update(self, feeds):
        '''[Internal]
        Searches for the shortest url in all the feeds. This is probably
        the main feed (url). It will also update the feed list and mark the
        shortest feed as the main one.
        If feeds is None or feeds is an empty list (e. g. []) then None is
        returned. Otherwise the shortest feed will be returned.'''
        if feeds is None or feeds == []:
            return None
        shortest_feed = feeds[0]
        shortest_feed_length = len(shortest_feed.url)
        for feed in feeds:
            if len(feed.url) < shortest_feed_length:
                shortest_feed = feed
                shortest_feed_length = len(shortest_feed.url)
        shortest_feed.is_main = True
        return shortest_feed

    def _find_feeds_in_header(self, html):
        '''[Internal]
        Parses the given HTML string with BeautifulSoup4 and searches for
        either RSS or Atom feed URLs. If both are available they will be
        concatenated. If no feed URL is found, an empty list will be returned.
        '''
        soup = BeautifulSoup(html, 'html.parser')
        feeds = []
        feeds += self._find_rss_feeds_in_header(soup)
        feeds += self._find_atom_feeds_in_header(soup)
        return feeds

    def find_feeds(self, url):
        '''Tries to find RSS or Atom feed for the given URL.
        Returns an empty list if no URL was found.'''
        try:
            html = self._get_html(url)
            feeds = self._find_feeds_in_header(html)
            return feeds
        except ValueError as e:
            if DEBUG:
                import traceback
                print(traceback.format_exc().splitlines()[-1])
            return []
        except:
            if DEBUG:
                import traceback
                print(traceback.format_exc())
            return []

    def find_feeds_m(self, urls):
        '''Tries to find feeds for a list of URLs. Groups the results for each
        URL.'''
        result = {}
        urls = urls if urls is not None else []
        for url in urls:
            result[url] = self.find_feeds(url)
        return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('>> No url parameter given!')
        print('>> Execute:\n     %s url1 [url2 [...]]' % sys.argv[0])
        quit(1)

    url_s = sys.argv[1:]
    result = FeedFinder().find_feeds_m(url_s)
    for url, feeds in result.items():
        print(url)
        for feed in feeds:
            print(' %s  %s - %s' % (('*' if feed.is_main else ' '),
                feed.url, feed.title))
        print()
