#!/usr/bin/env python

from bs4 import BeautifulSoup as bs
import urllib

url = "http://b.hatena.ne.jp/hotentry"
content = urllib.urlopen(url).read()
soup = bs(content)
links = soup.find_all("a",{"class":"entry-link"})
for link in links:
    print link["href"]