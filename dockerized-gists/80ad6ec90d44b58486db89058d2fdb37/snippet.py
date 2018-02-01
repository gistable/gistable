#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyleft (ↄ) 2016 jkirchartz <me@jkirchartz.com>
#
# Distributed under terms of the NPL (Necessary Public License) license.

"""
Download all quotes from GoodReads by author's quote URL, print in fortune format
usage:
        python goodreadsquotes.py https://www.goodreads.com/author/quotes/1791.Seth_Godin > godin
"""

from pyquery import PyQuery
import sys, random, re, time


AUTHOR_REX = re.compile('\d+\.(\w+)$')

def grabber(base_url, i=1):
    url = base_url + "?page=" + str(i)
    page = PyQuery(url)
    quotes = page(".quoteText")
    auth_match = re.search(AUTHOR_REX, base_url)
    if auth_match:
      author = re.sub('_', ' ', auth_match.group(1))
    else:
      author = False
    # sys.stderr.write(url + "\n")
    for quote in quotes.items():
        quote = quote.remove('script').text().encode('ascii', 'ignore')
        if author:
          quote = quote.replace(author, " -- " + author)
        print quote
        print '%'

    if not page('.next_page').hasClass('disabled'):
      time.sleep(10)
      grabber(base_url, i + 1)

if __name__ == "__main__":
  grabber(''.join(sys.argv[1:]))
