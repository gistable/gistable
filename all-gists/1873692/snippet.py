#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run this:

1. Download BeautifulSoup 3.2.0:
   http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.2.0.tar.gz

2. I unzipped it into a folder named "bs3", then touched an "__init__.py" file in that folder to make it a package.

3. Then place this file in the parent directory, so you've got something like this:

    .
    ├── bs3
    │   ├── BeautifulSoup.py
    │   ├── BeautifulSoupTests.py
    │   ├── PKG-INFO
    │   ├── __init__.py
    │   └── setup.py
    ├── cnn.py

"""

import codecs
import requests
from bs3.BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
#from bs4 import BeautifulSoup # :(

def scrape(url="http://money.cnn.com/2012/02/20/news/economy/david_walker_third_party/index.htm"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content)

    container = soup.find("div", id="storytext")
    content_list = [p.string for p in container.findAll("p") if p.string]
    content = "\n".join(content_list)

    # Also convert any HTML or XML entitied
    stoned_content = BeautifulStoneSoup(content, 
        convertEntities=BeautifulStoneSoup.ALL_ENTITIES)

    return "".join(stoned_content.contents)

def to_file(filename="cnn.txt"):
    f = codecs.open(filename, encoding="utf-8", mode="w")
    f.write(scrape())
    f.close()


if __name__ == "__main__":
    print "Fetching content from http://money.cnn.com/2012/02/20/news/economy/david_walker_third_party/index.htm ... "
    to_file()
    print "done. Check out cnn.txt"

