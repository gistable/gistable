#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Danilo de Jesus da Silva Bellini
# Created on Thu Apr 18 2013
"""
Prints all programming languages (from Wikipedia)
"""

from bs4 import BeautifulSoup # Needs "pip install beautifulsoup4"
from urllib2 import Request, build_opener

url = "http://en.wikipedia.org/wiki/List_of_programming_languages"
ff_string = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
req = Request(url, headers={"User-Agent": ff_string})
data = build_opener().open(req).read()

for link in BeautifulSoup(data).select(".multicol a"):
  print link.text