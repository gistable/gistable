#! /usr/bin/env python
# -*- coding: utf-8 -*-

# blookup.py
# by Caleb McDaniel <http://wcm1.web.rice.edu>

# Uses ottobib.com and isbndb.com to turn an author-title search string
# into a formatted bibliographic citation.
# Example:
#   blookup.py "blight race and reunion"
# 	>>> Blight, David W. *Race and reunion : the Civil War in American
#	memory*. Cambridge, Mass: Belknap Press of Harvard University Press, 2001.

import sys
import urllib
import urllib2

# We'll be parsing XML with BS4, so you need to install BeautifulSoup and lxml.
# e.g., `sudo pip install beautifulsoup4` and `sudo pip install lxml`
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#parser-installation

from bs4 import BeautifulSoup

# We'll also be converting HTML output to markdown.
# For this, I use Pandoc and https://github.com/kennethreitz/pyandoc
# With some minor script tweaking, you could eliminate markdown conversion
# and just get HTML output from OttoBib. See end of script for details.

import pandoc

# SETTINGS -----------------------------------------------------------------

# We will use the isbndb.com API, so you need to create an account.
# Once logged in to isbndb.com, create an access key and enter it here.
# By default, you are limited to 500 searches a day using this key.

accesskey = "XXXXXXXX"

# OttoBib can produce output in several styles. Pick your poison.
# http://www.ottobib.com/about

style = "chicago" # mla / apa

# --------------------------------------------------------------------------

# Encode the search string for isbndb.com.
query = urllib.quote_plus(sys.argv[1])

# Search isbndb.com for string.
isbndburl = "http://isbndb.com/api/books.xml?access_key=" + accesskey + "&index1=combined&value1=" + query
xml = urllib2.urlopen(isbndburl).read()

# Use BS4 to get ISBN of top search result.
soup = BeautifulSoup(xml, "xml")
tag = soup.BookData
bookisbn = tag['isbn']

# Search ottobib.com for ISBN.
ottobiburl = "http://www.ottobib.com/isbn/" + bookisbn + "/" + style
html = urllib2.urlopen(ottobiburl).read()

# Use BS4 to get the formatted citation returned by OttoBib
osoup = BeautifulSoup(html)
for br in osoup.find_all(name='br'):
	br.decompose()
citation = osoup.find("div", class_="nine columns")

# Convert OttoBib's formatted citation from HTML to Markdown using Pandoc.
doc = pandoc.Document()
doc.html = str(citation)
citation = doc.markdown

# Print the Markdown citation, removing newlines.
print citation.replace('\n', ' ')

# Or, if you don't want Markdown, comment out lines 70-75 and uncomment 78:
# print citation 
