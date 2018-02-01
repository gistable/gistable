#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


"""
    Tools to extract feed links, test if they are valid and parse them 
    with feedparser, returning content or a proper error.
"""

import urllib2

import feedparser

from BeautifulSoup import BeautifulSoup


# list of attributes that can have a feed link in the <HEAD> section
# so we can identify at least one in a page
FEED_LINKS_ATTRIBUTES = (
    (('type', 'application/rss+xml'),),
    (('type', 'application/atom+xml'),),
    (('type', 'application/rss'),),
    (('type', 'application/atom'),),
    (('type', 'application/rdf+xml'),),
    (('type', 'application/rdf'),),
    (('type', 'text/rss+xml'),),
    (('type', 'text/atom+xml'),),
    (('type', 'text/rss'),),
    (('type', 'text/atom'),),
    (('type', 'text/rdf+xml'),),
    (('type', 'text/rdf'),),
    (('rel', 'alternate'), ('type', 'text/xml')),
    (('rel', 'alternate'), ('type', 'application/xml')),
)


def extract_feed_links(html, feed_links_attributes=FEED_LINKS_ATTRIBUTES):
    """
        Return a generator yielding potiential feed links in a HTML page.

        >>> url = urllib2.urlopen('http://www.codinghorror.com/blog/')
        >>> links = extract_feed_links(url.read(1000000))
        >>> tuple(links)
        (u'http://feeds.feedburner.com/codinghorror/',)
    """
    soup = BeautifulSoup(html)
    head = soup.find('head')
    links = []
    for attrs in feed_links_attributes:
        for link in head.findAll('link', dict(attrs)):
            href = dict(link.attrs).get('href', '')
            if href: 
                yield unicode(href)


def get_first_working_feed_link(url):
    """
        Try to use the current URL as a feed. If it works, returns it.
        It it doesn't, load the HTML and try to get links from it then
        test them one by one and returns the first one that works.

        >>> get_first_working_feed_link('http://www.codinghorror.com/blog/')
        u'http://feeds.feedburner.com/codinghorror/'
        >>> get_first_working_feed_link('http://feeds.feedburner.com/codinghorror/')
        u'http://feeds.feedburner.com/codinghorror/'
    """

    # if the url is a feed itself, returns it
    html = urllib2.urlopen(url).read(1000000)
    feed = feedparser.parse(html)
    
    if not feed.get("bozo", 1):
        return unicode(url)

    # construct the site url from the domain name and the protocole name    
    parsed_url = urllib2.urlparse.urlparse(url)
    site_url = u"%s://%s" % (parsed_url.scheme, parsed_url.netloc)
    
    # parse the html extracted from the url, and get all the potiential
    # links from it then try them one by one
    for link in extract_feed_links(html):
        if '://' not in link: # if we got a relative URL, make it absolute 
            link = site_url + link
        feed = feedparser.parse(link)
        if not feed.get("bozo", 1):
            return link

    return None


if __name__ == "__main__":
    import doctest
    doctest.testmod()