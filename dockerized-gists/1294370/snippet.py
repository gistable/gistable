#!/usr/bin/python
from BeautifulSoup import BeautifulSoup
import sys

soup = BeautifulSoup(sys.stdin.read())
print soup.prettify()